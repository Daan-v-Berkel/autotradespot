import time

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import *
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from config.settings import base as settings
from portfolios.users import forms as user_forms

from . import forms, models
from .tasks import *

# Create your views here.

CustomUser = get_user_model()


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


def RegisterUser(request):
    page = "register"
    form = user_forms.UserSignupForm()

    if request.method == "POST":
        form = user_forms.UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect("autotradespot:home")

    context = {"page": page, "form": form}
    return render(request, "login_register.html", context)


def LoginPage(request):
    page = "login"
    form = forms.LoginForm()

    if request.method == "POST":
        login_used = request.POST.get("username")
        mail_used = "@" in login_used
        password = request.POST.get("password")

        try:
            user_obj = (
                models.CustomUser.objects.get(email=login_used)
                if mail_used
                else models.CustomUser.objects.get(username=login_used)
            )
        except:
            messages.warning(request, f'there is no user registered under "{login_used}"')
            user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)
                next_url = request.GET.get("next", "home")
                return redirect(f"autotradespot:{next_url}")

    context = {"page": page, "form": form}
    return render(request, "login_register.html", context)


def LogoutPage(request):
    logout(request)
    return redirect("autotradespot:home")


def Home(request):
    ads = models.Advertisement.objects.filter(status__exact=1)[:6].prefetch_related("imagemodel_set")
    context = {"advertisements": ads}
    return render(request, "index.html", context)


def Ad(request, pk):
    ad = models.Advertisement.objects.prefetch_related("imagemodel_set").get(id=pk)
    if request.user != ad.owner and not request.session.get(f"ad_viewed_{ad.pk}", False):
        request.session[f"ad_viewed_{ad.pk}"] = "true"
        ad.increment_views()
    return render(request, "advertisement.html", context={"advertisement": ad})


@login_required(login_url="autotradespot:login")
def ProfilePage(request):
    return render(request, "user_profile.html")


@login_required(login_url="login")
def UserPreferences(request):
    saved = None
    preferences = models.UserCustomisation.objects.get(user=request.user)
    form = forms.UserPreferenceForm(instance=preferences)
    if request.method == "POST":
        form = forms.UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save(commit=True)
            saved = _("Your preferences have been saved succesfully!")
    return render(request, "partials/user_pages/preferences.html", context={"preferences": form, "saved": saved})


@login_required(login_url="login")
def UserProfile(request):
    saved = None
    form = user_forms.UserChangeForm(instance=request.user)
    if request.method == "POST":
        form = user_forms.UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(commit=True)
            saved = _("Your profile has been saved succesfully!")
    return render(request, "partials/user_pages/profile.html", context={"profile": form, "saved": saved})


@login_required(login_url="login")
def UserFavourites(request):
    listings = request.user.favourites_list.all()
    return render(request, "partials/user_pages/favorites.html", context={"listings": listings})


@login_required(login_url="login")
def UserListings(request):
    listings = models.Advertisement.objects.filter(owner=request.user).order_by("status")
    return render(
        request, "partials/user_pages/advertisements.html", context={"listings": listings, "page": "profile"}
    )


@login_required(login_url="login")
def AddToFavorites(request, pk):
    ad = models.Advertisement.objects.get(pk=pk)
    if request.method == "POST":
        if ad.favourites_list.contains(request.user):
            ad.favourites_list.remove(request.user)
        else:
            ad.favourites_list.add(request.user)
        return render(request, "widgets/favourite_but.html", context={"ad": ad})


@login_required(login_url="account_login")
def CreateAdNew(request, save_method=None):
    if request.method == "DELETE":
        try:
            del request.session["ad_in_progress"]
        except:
            pass
        try:
            del request.session["LP_data"]
        except:
            pass
        page = render(request, "createad.html")
        page.headers["HX-Refresh"] = "true"
        return page
    ad_pk = request.session.get("ad_in_progress", False)
    if request.method == "PUT" and ad_pk:
        ad = models.Advertisement.objects.get(pk=ad_pk)
        if save_method == "draft":
            ad.status = ad.Status.DRAFT
            ad.save()
        elif save_method == "final":
            if ad.complete_for_posting:
                ad.status = ad.Status.ACTIVE
                ad.save()
                return HTTPResponseHXRedirect(redirect_to=reverse_lazy("autotradespot:advertisement", args=(ad_pk,)))
    elif request.method == "PUT" and not ad_pk:
        return HttpResponse("error saving, minimum requirements not met to save the listing")
    return render(request, "createad.html")


def CreateAdLicence(request):
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
        return redirect("autotradespot:createadtype")
    else:
        context = {"licence": request.session.get("LP_data", {"licence": ""})["licence"]}
        return render(request, "createadLP.html", context)


def CreateAdType(request):
    if request.method == "POST":
        form = forms.AdvertisementForm(request.POST)
        type = request.POST.get("type")
        if type == "S":
            priceform = forms.PricingSaleForm(request.POST)
        elif type == "L":
            priceform = forms.PricingLeaseForm(request.POST)
        if form.is_valid() and priceform.is_valid():
            ad, created = models.Advertisement.objects.update_or_create(
                pk=request.session.get("ad_in_progress"), defaults=form.cleaned_data | {"owner": request.user}
            )
            if type == "S":
                p, c = models.PricingModelBuy.objects.update_or_create(
                    listing=ad, defaults=priceform.cleaned_data | {"listing": ad}
                )
            elif type == "L":
                p, c = models.PricingModelLease.objects.update_or_create(
                    listing=ad, defaults=priceform.cleaned_data | {"listing": ad}
                )
            request.session["ad_in_progress"] = ad.pk
            return redirect("autotradespot:createadmake")
        else:
            return render(request, "createadtype.html", context={"form1": form, "priceform": priceform})

    if "ad_in_progress" in request.session:
        current_ad = models.Advertisement.objects.get(pk=request.session.get("ad_in_progress"))
        form = forms.AdvertisementForm(instance=current_ad)
    elif "LP_data" in request.session:
        substitute_title = f"{request.session['LP_data']['make']} {request.session['LP_data']['model']}"
        form = forms.AdvertisementForm(initial={"title": substitute_title})
    else:
        form = forms.AdvertisementForm()
    priceform = forms.PricingLeaseForm
    return render(request, "createadtype.html", context={"form1": form, "priceform": priceform})


def CreateAdMake(request):
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
            # make = make_form.save(commit=True)
            # model = model_form.save(commit=False)
            # model.make = make
            # model.save()
            return redirect("autotradespot:createaddetails")
        return render(request, "createadmake.html", context={"make_form": make_form, "model_form": model_form})

    # if 'ad_in_progress' in request.session:
    #     current_ad = models.Advertisement.objects.get(pk=request.session.get('ad_in_progress'))
    #     form2 = forms.CarMakeForm(instance=current_ad)
    #     form3 = forms.CarModelForm(instance=current_ad)
    # if 'LP_data' in request.session:
    #     form2 = forms.CarMakeForm(initial=request.session['LP_data'])
    #     form3 = forms.CarModelForm(initial=request.session['LP_data'])
    # else:
    make = request.GET.get("make", 0)
    nqs = models.CarModel.objects.filter(make=make)
    make_form = forms.CarMakeForm()
    model_form = forms.CarModelForm(nqs=nqs, disabled=True)
    return render(request, "createadmake.html", context={"make_form": make_form, "model_form": model_form})


def CreateAdDetails(request):
    if request.method == "POST":
        details_form = forms.CardetailForm(request.POST)
        if details_form.is_valid():
            current_ad = models.Advertisement.objects.get(pk=request.session.get("ad_in_progress"))
            make = models.CarMake.objects.get(pk=request.session["LP_data"]["makeId"])
            model = models.CarModel.objects.get(pk=request.session["LP_data"]["modelId"])
            details, created = models.CarDetails.objects.update_or_create(
                owning_advert=current_ad,
                defaults=details_form.cleaned_data | {"owning_advert": current_ad, "make": make, "model": model},
            )
            return redirect("autotradespot:uploadadimages")
        else:
            return render(request, "createaddetails.html", context={"form4": details_form})

    print(f'lp_data in cardetails: {request.session.get("LP_data")}')
    form4 = forms.CardetailForm(initial=request.session.get("LP_data") or {})
    if "ad_in_progress" in request.session:
        current_ad = models.Advertisement.objects.get(pk=request.session.get("ad_in_progress"))
        try:
            car_details = current_ad.cardetails
            form4 = forms.CardetailForm(instance=car_details)
        except:
            pass
    return render(request, "createaddetails.html", context={"form4": form4})


def UploadAdImages(request, image_pk=None):
    imageform = forms.AdvertisementImageForm()
    ad = models.Advertisement.objects.filter(pk=request.session.get("ad_in_progress", -1)).first()

    if request.method == "POST":
        imageform = forms.AdvertisementImageForm(request.POST, request.FILES)
        if imageform.is_valid():
            images = request.FILES.getlist("image")
            for i in images:
                models.ImageModel.objects.create(advertisement=ad, image=i)
            return redirect("autotradespot:advertisementpreview", ad_pk=ad.pk)

    elif request.method == "DELETE":
        print(f"trying to delete an image: {models.ImageModel.objects.get(pk=image_pk)}")
        models.ImageModel.objects.get(pk=image_pk).delete()

    return render(request, "uploadadimages.html", context={"imageform": imageform, "listing": ad})


def PreviewAdvertisement(request, ad_pk=-1):
    if ad_pk == -1:
        ad_pk = int(request.session.get("ad_in_progress") or 0)

    if int(ad_pk) < 1:
        ad = None
    else:
        ad = models.Advertisement.objects.get(pk=ad_pk)
    return render(request, "adpreview.html", context={"advertisement": ad})


def GetSelect(request):
    type = request.GET.get("type")
    if type == "S":
        form1 = forms.PricingSaleForm()
    elif type == "L":
        form1 = forms.PricingLeaseForm()
    else:
        return HttpResponse()
    return render(request, "pricingform.html", context={"form1": form1})


def ModifyListing(request, pk, action="modify"):
    ad = models.Advertisement.objects.get(pk=pk)

    if request.method == "DELETE":
        # ad.delete()
        return redirect("autotradespot:profile-page")

    elif request.method == "PUT":
        if action == "activate":
            complete, error_l = ad.complete_for_posting
            if complete:
                if ad.status == ad.Status.ACTIVE:
                    ad.status = ad.Status.INACTIVE
                else:
                    ad.status = ad.Status.ACTIVE
                ad.save()
            else:
                error_str = "\n".join(error_l)
                messages.warning(
                    request, f"this listing could not be acivated, please review the following:\n{error_str}"
                )
            page = render(
                request,
                "advertisement.html",
                context={"advertisement": ad, "favourites_cnt": len(ad.favourites_list.all())},
            )
            page.headers["HX-Refresh"] = "true"
            return page

        elif action == "modify":
            request.session["ad_in_progress"] = ad.pk
            return HTTPResponseHXRedirect(reverse_lazy("autotradespot:createadnew"))


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


def exceptiontest(request):
    raise ViewDoesNotExist("something wnent oopsie")


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


def getModels(request):
    make = request.GET.get("make", 0)
    form = forms.CarModelForm(nqs=models.CarModel.objects.filter(make=make))
    return HttpResponse(form)


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
