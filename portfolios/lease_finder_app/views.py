from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from portfolios.listings import models as ListingModels

def Home(request):
    listings = ListingModels.Listing.objects.filter(status__exact=1)[:6].prefetch_related("imagemodel_set")
    context = {"listings": listings}
    return render(request, "base/index.html", context)
