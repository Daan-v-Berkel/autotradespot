from django.urls import path

from portfolios.lease_finder_app import views

app_name = "autotradespot"
urlpatterns = [
    path("", views.Home, name="home"),
]
