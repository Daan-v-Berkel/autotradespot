from django.urls import path

from . import views

app_name = "listings"
urlpatterns = [
    path("test/", views.hello_world, name="hello_world"),
]
