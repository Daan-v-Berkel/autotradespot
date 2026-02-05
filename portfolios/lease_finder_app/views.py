from django.http import HttpResponse
from django.shortcuts import render

from portfolios.listings import models as ListingModels

# from django.utils.translation import gettext_lazy as _


def Home(request):
    listings = ListingModels.Listing.objects.filter(status__exact=1)[:6].prefetch_related("imagemodel_set")
    context = {"listings": listings}
    return render(request, "base/index.html", context)


def Cookies(request):
    request.session["cookies_accepted"] = "true"
    return HttpResponse("")


def HowItWorks(request):
    return render(request, "information/how_it_works.html")


def Test(request):
    return render(request, "testerpage.html")
