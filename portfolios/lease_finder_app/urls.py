from django.urls import path

from . import views

app_name = "autotradespot"
urlpatterns = [
    path("", views.Home, name="home"),
    path("register/", views.RegisterUser, name="register"),
    path("login/", views.LoginPage, name="login"),
    path("logout/", views.LogoutPage, name="logout"),
    path("ad/<str:pk>/", views.Ad, name="advertisement"),
    path("favorite/<str:pk>/", views.AddToFavorites, name="togglefavorite"),
    path("profile/", views.ProfilePage, name="profile-page"),
    path("profile/user", views.UserProfile, name="user_profile"),
    path("profile/preferences", views.UserPreferences, name="user_preferences"),
    path("profile/listings", views.UserListings, name="user_listings"),
    path("profile/favourites", views.UserFavourites, name="user_favourites"),
    path("make-listing/new", views.CreateAdNew, name="createadnew"),
    path("make-listing/new/<str:save_method>", views.CreateAdNew, name="createadnew"),
    path("make-listing/", views.CreateAdLicence, name="createadlicenceplate"),
    path("make-listing/type", views.CreateAdType, name="createadtype"),
    path("make-listing/make", views.CreateAdMake, name="createadmake"),
    path("make-listing/details", views.CreateAdDetails, name="createaddetails"),
    path("make-listing/images", views.UploadAdImages, name="uploadadimages"),
    path("make-listing/images/<int:image_pk>", views.UploadAdImages, name="uploadadimages"),
    path("make-listing/preview/<str:ad_pk>", views.PreviewAdvertisement, name="advertisementpreview"),
    path("make-listing/preview/", views.PreviewAdvertisement, name="advertisementpreview"),
    path("make-listing/type/getselect", views.GetSelect, name="getselect"),
    path("modify-listing/<int:pk>", views.ModifyListing, name="modify-listing"),
    path("modify-listing/<int:pk>/<str:action>", views.ModifyListing, name="modify-listing"),
    path("contact", views.contactView, name="contactform"),
    path("contact/cancel", views.contactCancelView, name="contactformcancel"),
    path("kaput", views.exceptiontest, name="testexception"),
    path("search", views.searchListing, name="searchlistings"),
    path("search/filters", views.searchfilters, name="filters"),
    path("models", views.getModels, name="getmodels"),
]
