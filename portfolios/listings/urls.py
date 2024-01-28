from django.urls import path

from . import views

app_name = "listings"
urlpatterns = [
    path("view/<int:pk>/", views.viewListing, name="viewlisting"),
    path("create/new", views.ListingCreateNew, name="createlistingnew"),
    path("create/new/<str:save_method>", views.ListingCreateNew, name="createlistingnew"),
    path("create/licenceplate", views.ListingLicenceplate, name="createlistinglicenceplate"),
    path("create/type", views.ListingType, name="createlistingtype"),
    path("create/make", views.ListingMake, name="createlistingmake"),
    path("create/details", views.ListingDetails, name="createlistingdetails"),
    path("create/images", views.ListingImages, name="uploadlistingimages"),
    path("create/images/<int:image_pk>", views.ListingImages, name="uploadlistingimages"),
    path("create/preview/<int:listing_pk>", views.PreviewListing, name="listingpreview"),
    path("create/preview/", views.PreviewListing, name="listingpreview"),
    path("create/type/getselect", views.GetSelect, name="getselect"),
    path("modify/<int:pk>", views.ModifyListing, name="modify-listing"),
    path("modify/<int:pk>/<str:action>", views.ModifyListing, name="modify-listing"),
    path("contact/", views.contactView, name="contactform"),
    path("contact/<int:pk>", views.contactView, name="contactform"),
    path("models/", views.getModels, name="getmodels"),
    path("models/<str:filter>", views.getModels, name="getmodels"),
    path("search", views.searchListing, name="searchlistings"),
    path("search/filter", views.FilterListings, name="searchfilters"),
]
