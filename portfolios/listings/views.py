import time

import requests
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import *

# from django.core.mail import BlistingHelistingerError, send_mail
from django.forms import modelformset_factory
from django.http import BadHeaderError, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from config.settings import base as settings
from portfolios.listings import forms, models

User = get_user_model()


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


def viewListing(request, pk):
    listing = models.Listing.objects.prefetch_related("imagemodel_set").get(pk=pk)
    if request.user != listing.owner and not request.session.get(f"listing_viewed_{listing.pk}", False):
        request.session[f"listing_viewed_{listing.pk}"] = "true"
        listing.increment_views()
    return render(request, "advertisement.html", context={"advertisement": listing})


@login_required(login_url="account_login")
def ListingCreateNew(request, save_method=None):
    if request.method == "DELETE":
        try:
            del request.session["listing_in_progress"]
        except:
            pass
        try:
            del request.session["LP_data"]
        except:
            pass
        page = render(request, "createad.html")
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
    return render(request, "createad.html")


def searchListing(request):
    makeformset = modelformset_factory(models.CarMake, can_delete=True, fields=["makeId"])
    make_form = forms.CarMakeFilter()
    model_form = forms.CarModelForm(nqs=models.CarModel.objects.none(), disabled=True)
    cardetail_form = forms.ListingFilter()

    if request.method == "POST":
        # make = request.POST.get('make', 0)
        # model = request.POST.get('model', 0)
        detailsform = forms.ListingFilter(request.POST)
        if detailsform.is_valid():
            listings = models.Advertisement.objects.search(**detailsform.cleaned_data)
            time.sleep(1)
            print(f"after post: {detailsform.cleaned_data}")
            return render(request, "ad_section.html", context={"advertisements": listings})

    return render(
        request,
        "searcher.html",
        context={
            "advertisements": models.Advertisement.objects.all(),
            "make_form": make_form,
            "model_form": model_form,
            "cardetail_form": cardetail_form,
            "formset": makeformset,
        },
    )


def ListingLicenceplate(request):
    if request.method == "POST":
        licenceplate = request.POST["licenceplate"].upper()
        data = requests.get(
            "http://opendata.rdw.nl/resource/m9d7-ebf2.json?" f"kenteken={licenceplate}",
            headers={"X-App-Token": settings.CARDATA_API_APP_TOKEN},
        ).json()[0]

        data1 = requests.get(
            "https://opendata.rdw.nl/resource/8ys7-d773.json?" f"kenteken={licenceplate}",
            headers={"X-App-Token": settings.CARDATA_API_APP_TOKEN},
        ).json()[0]

        data_combined = data | data1
        relevant_data = {"licence": licenceplate}
        # only store relevant data in session
        for name, api_name in settings.RELEVANT_CARDATA_FIELDS.items():
            relevant_data[name] = data_combined.get(api_name)

        request.session["LP_data"] = relevant_data
        return redirect("listings:createadtype")
    else:
        context = {"licence": request.session.get("LP_data", {"licence": ""})["licence"]}
        return render(request, "createadLP.html", context)


def ListingType(request):
    if request.method == "POST":
        form = forms.ListingForm(request.POST)
        type = request.POST.get("type")
        if type == "S":
            priceform = forms.PricingSaleForm(request.POST)
        elif type == "L":
            priceform = forms.PricingLeaseForm(request.POST)
        if form.is_valid() and priceform.is_valid():
            ad, created = models.Listing.objects.update_or_create(
                pk=request.session.get("listing_in_progress"), defaults=form.cleaned_data | {"owner": request.user}
            )
            if type == "S":
                p, c = models.PricingModelBuy.objects.update_or_create(
                    listing=ad, defaults=priceform.cleaned_data | {"listing": ad}
                )
            elif type == "L":
                p, c = models.PricingModelLease.objects.update_or_create(
                    listing=ad, defaults=priceform.cleaned_data | {"listing": ad}
                )
            request.session["listing_in_progress"] = ad.pk
            return redirect("listings:createadmake")
        else:
            return render(request, "createadtype.html", context={"form1": form, "priceform": priceform})

    if "listing_in_progress" in request.session:
        current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
        form = forms.ListingForm(instance=current_listing)
    elif "LP_data" in request.session:
        substitute_title = f"{request.session['LP_data']['make']} {request.session['LP_data']['model']}"
        form = forms.ListingForm(initial={"title": substitute_title})
    else:
        form = forms.ListingForm()
    priceform = forms.PricingLeaseForm
    return render(request, "createadtype.html", context={"form1": form, "priceform": priceform})


def ListingMake(request):
    if request.method == "POST":
        make_form = forms.CarMakeForm(request.POST)
        model_form = forms.CarModelForm(
            request.POST, nqs=models.CarModel.objects.filter(make=request.POST.get("make", 0))
        )
        if make_form.is_valid() and model_form.is_valid():
            d = request.session.get("LP_data", {})
            d["makeId"] = request.POST.get("make", 0)
            d["modelId"] = request.POST.get("model", 0)
            request.session["LP_data"] = d
            return redirect("listings:createaddetails")
        return render(request, "createadmake.html", context={"make_form": make_form, "model_form": model_form})

    make = request.GET.get("make", 0)
    nqs = models.CarModel.objects.filter(make=make)
    make_form = forms.CarMakeForm()
    model_form = forms.CarModelForm(nqs=nqs, disabled=True)
    return render(request, "createadmake.html", context={"make_form": make_form, "model_form": model_form})


def ListingDetails(request):
    if request.method == "POST":
        details_form = forms.CardetailForm(request.POST)
        if details_form.is_valid():
            current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
            make = models.CarMake.objects.get(pk=request.session["LP_data"]["makeId"])
            model = models.CarModel.objects.get(pk=request.session["LP_data"]["modelId"])
            details, created = models.CarDetails.objects.update_or_create(
                owning_advert=current_listing,
                defaults=details_form.cleaned_data | {"owning_advert": current_listing, "make": make, "model": model},
            )
            return redirect("listings:uploadadimages")
        else:
            return render(request, "createaddetails.html", context={"form4": details_form})

    print(f'lp_data in cardetails: {request.session.get("LP_data")}')
    form4 = forms.CardetailForm(initial=request.session.get("LP_data") or {})
    if "listing_in_progress" in request.session:
        current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
        try:
            car_details = current_listing.cardetails
            form4 = forms.CardetailForm(instance=car_details)
        except:
            pass
    return render(request, "createaddetails.html", context={"form4": form4})


def ListingImages(request, image_pk=None):
    imageform = forms.ListingImageForm()
    listing = models.Listing.objects.filter(pk=request.session.get("listing_in_progress", -1)).first()

    if request.method == "POST":
        imageform = forms.ListingImageForm(request.POST, request.FILES)
        if imageform.is_valid():
            images = request.FILES.getlist("image")
            for i in images:
                models.ImageModel.objects.create(listing=listing, image=i)
            return redirect("listings:advertisementpreview", ad_pk=listing.pk)

    elif request.method == "DELETE":
        print(f"trying to delete an image: {models.ImageModel.objects.get(pk=image_pk)}")
        models.ImageModel.objects.get(pk=image_pk).delete()

    return render(request, "uploadadimages.html", context={"imageform": imageform, "listing": listing})


def PreviewListing(request, listing_pk=-1):
    if listing_pk == -1:
        listing_pk = int(request.session.get("listing_in_progress") or 0)

    if int(listing_pk) < 1:
        listing = None
    else:
        listing = models.Listing.objects.get(pk=listing_pk)
    return render(request, "adpreview.html", context={"advertisement": listing})


def GetSelect(request):
    # TODO: rename
    type = request.GET.get("type")
    if type == "S":
        form1 = forms.PricingSaleForm()
    elif type == "L":
        form1 = forms.PricingLeaseForm()
    else:
        return HttpResponse()
    return render(request, "pricingform.html", context={"form1": form1})


def ModifyListing(request, pk, action="modify"):
    listing = models.Listing.objects.get(pk=pk)

    if request.method == "DELETE":
        # listing.delete()
        return redirect("autotradespot:profile-page")

    elif request.method == "PUT":
        if action == "activate":
            complete, error_l = listing.complete_for_posting
            if complete:
                if listing.status == listing.Status.ACTIVE:
                    listing.status = listing.Status.INACTIVE
                else:
                    listing.status = listing.Status.ACTIVE
                listing.save()
            else:
                error_str = "\n".join(error_l)
                messages.warning(
                    request, f"this listing could not be acivated, please review the following:\n{error_str}"
                )
            page = render(
                request,
                "advertisement.html",
                context={"advertisement": listing, "favourites_cnt": len(listing.favourites_list.all())},
            )
            page.headers["HX-Refresh"] = "true"
            return page

        elif action == "modify":
            request.session["listing_in_progress"] = listing.pk
            return HTTPResponseHXRedirect(reverse_lazy("listings:createadnew"))


def contactView(request):
    if request.method == "GET":
        umail = request.user.email if request.user.is_authenticated else ""
        subject = _("Interest in your listing")
        message = _(
            f"Hi there,\n\nI am interested in your listing on Auto Tradespot!\nPlease contact me by replying to this email.\n\nWith regards, {request.user.username}"
        )
        form = forms.ContactForm(initial={"from_email": umail, "subject": subject, "message": message})
    else:
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            try:
                form.send_email()
                # html_message = render_to_string('emails/welcome.html')
                # plain_message = strip_tags(html_message)
                # send_mail(subject, plain_message, from_email, ["admin@example.com"])#, html_message=html_message)
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return HttpResponse(_("Thank you for your interest, the provider of this listing will contact you soon!"))
    return render(request, "partials/contact/contact_form.html", {"form": form})


def contactCancelView(request):
    return render(request, "partials/contact/contact_btn.html")


def searchfilters(request):
    make = request.POST.get("make", 0)
    print(f"filter: {type( make)}")
    if int(make) <= 0:
        nqs = models.CarModel.objects.none()
    else:
        makeid = models.CarMake.objects.get(makeId=make) if make != 0 else 0
        nqs = models.CarModel.objects.filter(make=makeid)
    model_form = forms.CarModelFilter(nqs=nqs, disabled=False)
    return HttpResponse(model_form)


def getModels(request):
    make = request.GET.get("make", 0)
    form = forms.CarModelForm(nqs=models.CarModel.objects.filter(make=make))
    return HttpResponse(form)
