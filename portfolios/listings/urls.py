from django.urls import path

from . import views

app_name = "listings"
urlpatterns = [
    path("view/<int:pk>/", views.viewListing, name="viewlisting"),
    path("create/new", views.ListingCreateNew, name="createadnew"),
    path("create/new/<str:save_method>", views.ListingCreateNew, name="createadnew"),
    path("search", views.searchListing, name="searchlistings"),
    # path("search/filters", views.searchfilters, name="filters"),
    path("create/licenceplate", views.ListingLicenceplate, name="createadlicenceplate"),
    path("create/type", views.ListingType, name="createadtype"),
    path("create/make", views.ListingMake, name="createadmake"),
    path("create/details", views.ListingDetails, name="createaddetails"),
    path("create/images", views.ListingImages, name="uploadadimages"),
    path("create/images/<int:image_pk>", views.ListingImages, name="uploadadimages"),
    path("create/preview/<str:ad_pk>", views.PreviewListing, name="advertisementpreview"),
    path("create/preview/", views.PreviewListing, name="advertisementpreview"),
    path("create/type/getselect", views.GetSelect, name="getselect"),
    path("modify/<int:pk>", views.ModifyListing, name="modify-listing"),
    path("modify/<int:pk>/<str:action>", views.ModifyListing, name="modify-listing"),
    path("contact/", views.contactView, name="contactform"),
    path("contact/<int:pk>", views.contactView, name="contactform"),
    path("contact/cancel", views.contactCancelView, name="contactformcancel"),
    path("models", views.getModels, name="getmodels"),
]
