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
from portfolios.lease_finder_app import forms, models
from portfolios.listings import models as ListingModels
from portfolios.users import forms as user_forms

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
    listings = ListingModels.Listing.objects.filter(status__exact=1)[:6].prefetch_related("imagemodel_set")
    context = {"advertisements": listings}
    return render(request, "index.html", context)


@login_required(login_url="account_login")
def ProfilePage(request):
    return render(request, "user_profile.html")


@login_required(login_url="account_login")
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


@login_required(login_url="account_login")
def UserProfile(request):
    saved = None
    form = user_forms.UserChangeForm(instance=request.user)
    if request.method == "POST":
        form = user_forms.UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(commit=True)
            saved = _("Your profile has been saved succesfully!")
    return render(request, "partials/user_pages/profile.html", context={"profile": form, "saved": saved})


@login_required(login_url="account_login")
def UserFavourites(request):
    listings = request.user.favourites_list.all()
    return render(request, "partials/user_pages/favorites.html", context={"listings": listings})


@login_required(login_url="account_login")
def UserListings(request):
    listings = ListingModels.Listing.objects.filter(owner=request.user).order_by("status")
    return render(
        request, "partials/user_pages/advertisements.html", context={"listings": listings, "page": "profile"}
    )


@login_required(login_url="account_login")
def AddToFavorites(request, pk):
    listing = ListingModels.Listing.objects.get(pk=pk)
    if request.method == "POST":
        if listing.favourites_list.contains(request.user):
            listing.favourites_list.remove(request.user)
        else:
            listing.favourites_list.add(request.user)
        return render(request, "widgets/favourite_but.html", context={"listing": listing})


def exceptiontest(request):
    raise ViewDoesNotExist("something wnent oopsie")
