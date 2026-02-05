from django.urls import path

from portfolios.users import views

app_name = "users"
urlpatterns = [
    # path("~redirect/", view=user_redirect_view, name="redirect"),
    # path("~update/", view=user_update_view, name="update"),
    path("my-profile/", view=views.user_detail_view, name="detail"),
    path("profile/user", views.UserProfile, name="user_profile"),
    path("profile/preferences", views.UserPreferences, name="user_preferences"),
    path("profile/listings", views.UserListings, name="user_listings"),
    path("profile/favourites", views.UserFavourites, name="user_favourites"),
    path("favorite/<int:pk>/", views.AddToFavorites, name="togglefavorite"),
]
