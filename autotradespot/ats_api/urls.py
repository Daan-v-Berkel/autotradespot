from django.urls import path

from . import views

app_name = "ats_api"
urlpatterns = [
    path("test/", views.hello_world, name="hello_world"),
    path("listings/draft/", views.draft, name="draft"),
    path("listings/images/upload/", views.upload_images, name="upload_images"),
    path("listings/types/", views.listing_types, name="listing_types"),
    path("car/makes/", views.car_makes, name="car_makes"),
    path("car/models/", views.car_models, name="car_models"),
]
