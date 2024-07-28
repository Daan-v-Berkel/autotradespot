from django.urls import path

from portfolios.lease_finder_app import views

app_name = "autotradespot"
urlpatterns = [
    path("", views.Home, name="home"),
    path("cookies/", views.Cookies, name="cookies"),
    path("how-it-works/", views.HowItWorks, name="howitworks"),
    path("test/", views.Test, name="test"),
]
