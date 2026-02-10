import logging
import re
import time

import requests
from allauth.account.decorators import verified_email_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

# from django.core.mail import BlistingHelistingerError, send_mail
from django.forms import modelformset_factory
from django.http import BadHeaderError, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from autotradespot.listings import filters, forms, models
from autotradespot.listings.tasks import send_review_mail_task
from config.settings import base as settings

User = get_user_model()

logger = logging.getLogger(__name__)

# License plate validation regex for Dutch license plates
# Accepts formats: XX-XXX-XX, XXXXXX (with or without dashes)
DUTCH_LICENSE_PLATE_PATTERN = re.compile(
    r"^[A-Z0-9]{6}$|^[A-Z]{2}-?[0-9]{3}-?[A-Z]{2}$|^[0-9]{2}-?[A-Z]{2}-?[0-9]{2}$", re.IGNORECASE
)

# API configuration constants
API_TIMEOUT = 5  # seconds
API_ENDPOINTS = [
    "http://opendata.rdw.nl/resource/m9d7-ebf2.json",  # Voertuiginformatie
    "https://opendata.rdw.nl/resource/8ys7-d773.json",  # Gekentekende voertuigen
]


def validate_license_plate(license_plate: str) -> tuple[bool, str]:
    """
    Validate Dutch license plate format.

    Args:
        license_plate: The license plate to validate

    Returns:
        A tuple of (is_valid: bool, error_message: str)
    """
    if not license_plate:
        return False, _("License plate cannot be empty")

    # Remove spaces and dashes for validation
    cleaned_plate = license_plate.replace("-", "").replace(" ", "").upper()

    if len(cleaned_plate) != 6:
        return False, _("License plate must be 6 characters long")

    if not re.match(r"^[A-Z0-9]{6}$", cleaned_plate):
        return False, _("License plate must contain only letters and numbers")

    if not DUTCH_LICENSE_PLATE_PATTERN.match(cleaned_plate):
        return False, _("Invalid Dutch license plate format")

    return True, ""


def fetch_car_data_from_api(license_plate: str) -> tuple[bool, dict | None, str]:
    """
    Fetch car data from RDW API endpoints.

    Args:
        license_plate: The validated license plate

    Returns:
        A tuple of (success: bool, data: dict or None, error_message: str)
    """
    if not settings.CARDATA_API_APP_TOKEN:
        error_msg = _(
            "The license plate lookup service is temporarily unavailable. "
            "Please try again later or enter the car details manually."
        )
        logger.warning("CARDATA_API_APP_TOKEN not configured")
        return False, None, error_msg

    headers = {"X-App-Token": settings.CARDATA_API_APP_TOKEN}

    try:
        # Fetch from first API endpoint
        try:
            response1 = requests.get(
                f"{API_ENDPOINTS[0]}?kenteken={license_plate.upper()}",
                headers=headers,
                timeout=API_TIMEOUT,
            )
            response1.raise_for_status()
        except requests.exceptions.Timeout:
            error_msg = _(
                "The license plate lookup service is taking too long. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API timeout for license plate {license_plate} (endpoint 1)")
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = _(
                "Could not connect to the license plate lookup service. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API connection error for license plate {license_plate} (endpoint 1)")
            return False, None, error_msg
        except requests.exceptions.HTTPError as e:
            error_msg = _(
                "The license plate lookup service returned an error. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API HTTP error for license plate {license_plate} (endpoint 1): {e}")
            return False, None, error_msg

        # Fetch from second API endpoint
        try:
            response2 = requests.get(
                f"{API_ENDPOINTS[1]}?kenteken={license_plate.upper()}",
                headers=headers,
                timeout=API_TIMEOUT,
            )
            response2.raise_for_status()
        except requests.exceptions.Timeout:
            error_msg = _(
                "The license plate lookup service is taking too long. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API timeout for license plate {license_plate} (endpoint 2)")
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = _(
                "Could not connect to the license plate lookup service. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API connection error for license plate {license_plate} (endpoint 2)")
            return False, None, error_msg
        except requests.exceptions.HTTPError as e:
            error_msg = _(
                "The license plate lookup service returned an error. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"API HTTP error for license plate {license_plate} (endpoint 2): {e}")
            return False, None, error_msg

        # Parse responses
        try:
            data1 = response1.json()
            data2 = response2.json()
        except ValueError as e:
            error_msg = _(
                "The license plate lookup service returned invalid data. "
                "Please try again later or enter the car details manually."
            )
            logger.error(f"JSON decode error for license plate {license_plate}: {e}")
            return False, None, error_msg

        # Check if we have data from both endpoints
        if not (data1 and data2):
            error_msg = _(
                "No data found for license plate '{license_plate}'. " "Please make sure the license plate is correct."
            ).format(license_plate=license_plate)
            logger.info(f"No data found for license plate {license_plate}")
            return False, None, error_msg

        # Combine the data from both endpoints
        combined_data = data1[0] | data2[0]
        return True, combined_data, ""

    except Exception as e:
        error_msg = _(
            "An unexpected error occurred while looking up the license plate. "
            "Please try again later or enter the car details manually."
        )
        logger.exception(f"Unexpected error while fetching car data for {license_plate}: {e}")
        return False, None, error_msg


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


def viewListing(request, pk):
    listing = models.Listing.objects.prefetch_related("imagemodel_set").get(pk=pk)

    if listing.visible_to_public():
        if request.user != listing.owner:
            listing.increment_views()
    else:
        if not request.user.is_staff and not request.user == listing.owner:
            raise PermissionDenied()
    return render(request, "listings/base/listing.html", context={"listing": listing})


def clearListingInProgress(request):
    try:
        del request.session["listing_in_progress"]
    except KeyError:
        pass
    try:
        del request.session["LP_data"]
    except KeyError:
        pass


@login_required(login_url="account_login")
@verified_email_required
def ListingCreateNew(request, save_method=None):
    if request.method == "DELETE":
        clearListingInProgress(request)
        page = render(request, "listings/create/createlisting.html")
        page.headers["HX-Refresh"] = "true"
        return page

    listing_pk = request.session.get("listing_in_progress", False)
    if request.method == "PUT" and listing_pk:
        listing = models.Listing.objects.get(pk=listing_pk)
        if save_method == "draft":
            listing.status = listing.Status.DRAFT
            listing.save()
        elif save_method == "final":
            if listing.complete_for_posting:
                listing.status = listing.Status.ACTIVE
                listing.save()
                return HTTPResponseHXRedirect(redirect_to=reverse_lazy("listings:viewlisting", args=(listing_pk,)))
    elif request.method == "PUT" and not listing_pk:
        return HttpResponse("error saving, minimum requirements not met to save the listing")
    return render(request, "listings/create/createlisting.html")


def ListingLicenceplate(request):
    """
    Handle license plate lookup and car data retrieval.

    GET: Display the license plate form
    POST: Validate license plate format, fetch car data from API, and store in session
    """
    if request.method == "POST":
        license_plate_input = request.POST.get("licenceplate", "").strip()

        # Step 1: Validate license plate format (Issue #13)
        is_valid, validation_error = validate_license_plate(license_plate_input)
        if not is_valid:
            context = {
                "licence": license_plate_input,
                "licence_error": validation_error,
            }
            return render(request, "listings/create/createlistingLP.html", context)

        # Clean the license plate for API call
        clean_license_plate = license_plate_input.replace("-", "").replace(" ", "").upper()

        # Step 2: Fetch data from API with comprehensive error handling (Issue #14)
        success, combined_data, error_msg = fetch_car_data_from_api(clean_license_plate)
        if not success:
            context = {
                "licence": license_plate_input,
                "licence_error": error_msg,
            }
            return render(request, "listings/create/createlistingLP.html", context)

        # Step 3: Extract and store relevant data in session
        relevant_data = {"licence": clean_license_plate}
        for name, api_name in settings.RELEVANT_CARDATA_FIELDS.items():
            relevant_data[name] = combined_data.get(api_name)

        request.session["LP_data"] = relevant_data
        return redirect("listings:createlistingtype")
    else:
        context = {"licence": request.session.get("LP_data", {"licence": ""})["licence"]}
        return render(request, "listings/create/createlistingLP.html", context)


def ListingType(request):
    if request.method == "POST":
        form = forms.ListingForm(request.POST)
        type = request.POST.get("type")
        if type == "S":
            priceform = forms.PricingSaleForm(request.POST)
        elif type == "L":
            priceform = forms.PricingLeaseForm(request.POST)
        logger.debug("form_errors: %s", priceform.errors)
        if form.is_valid() and priceform.is_valid():
            listing, created = models.Listing.objects.update_or_create(
                pk=request.session.get("listing_in_progress"), defaults=form.cleaned_data | {"owner": request.user}
            )
            if type == "S":
                p, c = models.PricingModelBuy.objects.update_or_create(
                    listing=listing, defaults=priceform.cleaned_data | {"listing": listing}
                )
            elif type == "L":
                p, c = models.PricingModelLease.objects.update_or_create(
                    listing=listing, defaults=priceform.cleaned_data | {"listing": listing}
                )
            request.session["listing_in_progress"] = listing.pk
            return redirect("listings:createlistingmake")
        else:
            return render(
                request, "listings/create/createlistingtype.html", context={"form1": form, "priceform": priceform}
            )

    if "listing_in_progress" in request.session:
        current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
        form = forms.ListingForm(instance=current_listing)
    elif "LP_data" in request.session:
        substitute_title = f"{request.session['LP_data']['make']} {request.session['LP_data']['model']}"
        form = forms.ListingForm(initial={"title": substitute_title})
    else:
        form = forms.ListingForm()
    priceform = forms.PricingLeaseForm
    return render(request, "listings/create/createlistingtype.html", context={"form1": form, "priceform": priceform})


def ListingMake(request):
    if request.method == "POST":
        make_form = forms.CarMakeForm(request.POST)
        model_form = forms.CarModelForm(
            request.POST, nqs=models.CarModel.objects.filter(make=request.POST.get("make", 0))
        )
        variant_form = forms.VariantForm(request.POST)
        if make_form.is_valid() and model_form.is_valid() and variant_form.is_valid():
            d = request.session.get("LP_data", {})
            d["makeId"] = request.POST.get("make", 0)
            d["modelId"] = request.POST.get("model", 0)
            d["variant"] = variant_form.cleaned_data["variant"]
            request.session["LP_data"] = d
            return redirect("listings:createlistingdetails")
    else:
        make = request.GET.get("make", 0)
        nqs = models.CarModel.objects.filter(make=make)
        d = request.session.get("LP_data", {})
        if d:
            listing_make_qs = models.CarMake.objects.filter(name__iexact=d["make"])
            listing_make = listing_make_qs[0] if listing_make_qs else ""
            # listing_model_qs = models.CarModel.objects.filter(Q(name__iexact=d["model"]), Q(make=listing_make))
            # listing_model = listing_model_qs if listing_model_qs else ""
            make_form = forms.CarMakeForm(initial={"make": listing_make})
        else:
            make_form = forms.CarMakeForm()
        model_form = forms.CarModelForm(nqs=nqs, disabled=True)
        # model_form.data = {"model":listing_model}
        variant_form = forms.VariantForm()
    return render(
        request,
        "listings/create/createlistingmake.html",
        context={"make_form": make_form, "model_form": model_form, "variant_form": variant_form},
    )


def ListingDetails(request):
    if request.method == "POST":
        details_form = forms.CardetailForm(request.POST)
        caroptions_form = forms.CarOptionsForm(request.POST)
        if details_form.is_valid() and caroptions_form.is_valid():
            current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
            make = models.CarMake.objects.get(pk=request.session["LP_data"]["makeId"])
            model = models.CarModel.objects.get(pk=request.session["LP_data"]["modelId"])
            variant = request.session["LP_data"]["variant"]
            options = caroptions_form.cleaned_data["options"]
            details, created = models.CarDetails.objects.update_or_create(
                owning_listing=current_listing,
                defaults=details_form.cleaned_data
                | {"owning_listing": current_listing, "make": make, "model": model, "variant": variant},
            )
            logger.debug("detail_options: %s", options)
            details.options.set(options)
            return redirect("listings:uploadlistingimages")
        else:
            return render(
                request,
                "listings/create/createlistingdetails.html",
                context={"form4": details_form, "caroptions_form": caroptions_form},
            )

    logger.debug("lp_data in cardetails: %s", request.session.get("LP_data"))
    form4 = forms.CardetailForm(initial=request.session.get("LP_data") or {})
    caroptions_form = forms.CarOptionsForm()
    if "listing_in_progress" in request.session:
        current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
        try:
            car_details = current_listing.cardetails
            car_options = car_details.options
            form4 = forms.CardetailForm(instance=car_details)
            caroptions_form = forms.CarOptionsForm(instance=car_options)
        except models.CarDetails.DoesNotExist:
            pass
    return render(
        request,
        "listings/create/createlistingdetails.html",
        context={"form4": form4, "caroptions_form": caroptions_form},
    )


def ListingImages(request, image_pk=None):
    imageform = forms.ListingImageForm()
    listing = models.Listing.objects.filter(pk=request.session.get("listing_in_progress", -1)).first()

    if request.method == "POST":
        imageform = forms.ListingImageForm(request.POST, request.FILES)
        if imageform.is_valid():
            images = request.FILES.getlist("image")
            for i in images:
                models.ImageModel.objects.create(listing=listing, image=i)
            clearListingInProgress(request)
            return HTTPResponseHXRedirect(redirect_to=reverse_lazy("listings:viewlisting", args=(listing.pk,)))

    elif request.method == "DELETE":
        models.ImageModel.objects.get(pk=image_pk).delete()

    return render(
        request, "listings/create/uploadlistingimages.html", context={"imageform": imageform, "listing": listing}
    )


def GetPricingForm(request):
    type = request.GET.get("type")
    logger.debug("pricingtype: %s", type)
    if type == "S":
        form1 = forms.PricingSaleForm()
    elif type == "L":
        form1 = forms.PricingLeaseForm()
    else:
        return HttpResponse()
    return render(request, "listings/partials/pricingform.html", context={"form1": form1})


# def ModifyListing(request, pk, action="modify"):
#     listing = models.Listing.objects.get(pk=pk)

#     if request.method == "POST" and action == "delete":
#         listing.set_deleted()
#         return HTTPResponseHXRedirect(reverse_lazy("users:detail"))

#     elif request.method == "PUT":
#         if action == "activate":
#             listing.set_under_review()
#             page = render(
#                 request,
#                 "listings/base/listing.html",
#                 context={"listing": listing, "favourites_cnt": len(listing.favourites_list.all())},
#             )
#             page.headers["HX-Refresh"] = "true"
#             return page

#         elif action == "modify":
#             request.session["listing_in_progress"] = listing.pk
#             return HTTPResponseHXRedirect(reverse_lazy("listings:createlistingnew"))


def contactView(request, pk=None):
    listing = get_object_or_404(models.Listing, pk=pk)
    if request.method == "GET":
        umail = request.user.email if request.user.is_authenticated else ""
        subject = _("Interest in your listing")
        message = _(f"Hi there,\n\nI am interested in your listing on Auto Tradespot!\n\
Please contact me by replying to this email.\n\nWith regards, {request.user.name}")
        form = forms.ContactForm(initial={"from_email": umail, "subject": subject, "message": message})
    else:
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            try:
                form.send_email(recipient=listing.owner.email)
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return HttpResponse(_("Thank you for your interest, the provider of this listing will contact you soon!"))
    return render(request, "listings/contact/contact_form.html", {"form": form, "listing_pk": listing.pk})


def getModels(request, filter="filter"):
    make = request.GET.get("make", 0)
    if make:
        nqs = models.CarModel.objects.filter(make=make)
    else:
        nqs = models.CarMake.objects.all()
    if filter == "filter":
        form = filters.CarModelFilter(nqs=nqs)
    else:
        form = forms.CarModelForm(nqs=nqs)
    return HttpResponse(form)


def searchListing(request):
    # lm = models.Listing
    # base_qs = models.Listing.objects.filter(status__exact=lm.Status.ACTIVE, type__exact="S")
    leasetypefilter = filters.LeaseypeFilter()
    makefilter = filters.CarMakeFilter()
    modelfilter = filters.CarModelFilter(nqs=models.CarModel.objects.all())
    leasepricefilter = filters.LeasePriceFilter()
    salepricefilter = filters.SalePriceFilter()
    mileagesalefilter = filters.MileageSaleFilter()
    mileageleasefilter = filters.MileageLeaseFilter()
    leaseperiodfilter = filters.LeasePeriodFilter()
    context = {
        "leasetypefilter": leasetypefilter,
        "makefilter": makefilter,
        "modelfilter": modelfilter,
        "leasepricefilter": leasepricefilter,
        "salepricefilter": salepricefilter,
        "mileagesalefilter": mileagesalefilter,
        "mileageleasefilter": mileageleasefilter,
        "leaseperiodfilter": leaseperiodfilter,
    }
    return render(request, "listings/search/searcher.html", context=context)


@require_POST
def FilterListings(request):
    logger.debug("post dict: %s", request.POST.dict())
    qs = models.Listing.objects.search(searchdict=request.POST.dict())
    logger.debug("queryset: %s", qs)

    return render(request, "listings/search/listing_section_searchresults.html", context={"listings": qs})


# NEW LISTING CREATION ##
@login_required(login_url="account_login")
@verified_email_required
@ensure_csrf_cookie
def CreateListing(request):
    return render(request, "listings/create/base.html")
