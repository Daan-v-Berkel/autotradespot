from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

from autotradespot.listings import models as ListingModels
from autotradespot.users import forms, models

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile/user_profile.html"

    def get_object(self):
        return self.request.user


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = (
        "name",
        "email",
        "username",
    )
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"user": self.request.user})


user_redirect_view = UserRedirectView.as_view()


@login_required(login_url="account_login")
def ProfilePage(request):
    return render(request, "users/profile/user_profile.html")


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
    return render(request, "users/user_pages/preferences.html", context={"preferences": form, "saved": saved})


@login_required(login_url="account_login")
def UserProfile(request):
    saved = None
    form = forms.UserChangeForm(instance=request.user)
    if request.method == "POST":
        form = forms.UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save(commit=True)
            saved = _("Your profile has been saved succesfully!")
    return render(request, "users/user_pages/profile.html", context={"profile": form, "saved": saved})


@login_required(login_url="account_login")
def UserFavourites(request):
    listings = request.user.favourites_list.all()
    return render(request, "users/user_pages/favorites.html", context={"listings": listings})


@login_required(login_url="account_login")
def UserListings(request):
    listings = ListingModels.Listing.objects.filter(owner=request.user).order_by("status")
    return render(request, "users/user_pages/listings.html", context={"listings": listings, "page": "profile"})


@login_required(login_url="account_login")
def AddToFavorites(request, pk):
    listing = ListingModels.Listing.objects.get(pk=pk)
    if request.method == "POST":
        if listing.favourites_list.contains(request.user):
            listing.favourites_list.remove(request.user)
        else:
            listing.favourites_list.add(request.user)
        return render(request, "widgets/favourite_but.html", context={"listing": listing})
