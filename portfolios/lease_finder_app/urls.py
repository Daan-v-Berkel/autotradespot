from django.urls import path

from portfolios.lease_finder_app import views

app_name = "autotradespot"
urlpatterns = [
    path("", views.Home, name="home"),
    # path("register/", views.RegisterUser, name="register"),
    # path("login/", views.LoginPage, name="login"),
    # path("logout/", views.LogoutPage, name="logout"),
    path("favorite/<int:pk>/", views.AddToFavorites, name="togglefavorite"),
    path("profile/", views.ProfilePage, name="profile-page"),
    path("profile/user", views.UserProfile, name="user_profile"),
    path("profile/preferences", views.UserPreferences, name="user_preferences"),
    path("profile/listings", views.UserListings, name="user_listings"),
    path("profile/favourites", views.UserFavourites, name="user_favourites"),
    path("kaput", views.exceptiontest, name="testexception"),
]
