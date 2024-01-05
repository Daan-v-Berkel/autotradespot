from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from . import cardata

User = get_user_model()


# For complicated queries with filters
class ListingQuerySet(models.QuerySet):
    def search(self, **kwargs):
        qs = self
        if kwargs.get("fuel_type", []):
            qs = qs.filter(cardetails__fuel_type__in=kwargs["fuel_type"])
        if kwargs.get("transmission", []):
            qs = qs.filter(cardetails__transmission__in=kwargs["transmission"])
        if kwargs.get("num_doors", []):
            qs = qs.filter(cardetails__num_doors__in=kwargs["num_doors"])
        return qs


class Listing(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=3000, blank=True)
    available_from = models.DateField(default=timezone.now)
    favourites_list = models.ManyToManyField(User, related_name="favourites_list", blank=True, default=None)
    viewcount = models.IntegerField(default=0)

    objects = ListingQuerySet.as_manager()

    def increment_views(self):
        self.viewcount += 1
        self.save()

    created = models.DateField(editable=False)
    modified = models.DateField()

    class Status(models.IntegerChoices):
        INACTIVE = 0, _("Inactive")
        ACTIVE = 1, _("Active")
        DRAFT = 2, _("Draft")
        RESERVED = 3, _("Reserved")
        SOLD = 4, _("Sold")
        REMOVED = 5, _("Removed")
        REPORTED = 6, _("Reported")

    status = models.IntegerField(choices=Status.choices, default=Status.INACTIVE)

    @property
    def status_name(self):
        return self.Status.choices[self.status][1]

    def explain_errors(self, errors):
        if not errors:
            return ""
        error_lib = {
            "status": _(f"this listing hs been {self.status_name} and cannot be changed at this time."),
            "pricing": _(
                f"this listing has no pricing details, these are needed before being able to activate the listing."
            ),
            "images": _(f"this listing has either no images, or the images do not meet the minimum requirements"),
            "details": _(f"this listing has insufficient details about the listed object"),
        }
        return [str(v) for k, v in error_lib.items() if k in errors]

    @property
    def complete_for_posting(self):
        pricing_types = {"S": "price_model_S", "L": "price_model_L"}
        error_lib = {
            "status": self.status not in [5, 6],
            "pricing": getattr(self, pricing_types[self.type], None) != None,
            "images": bool(self.imagemodel_set.all()),
            "details": hasattr(self, "cardetails"),
        }
        b = all(error_lib.values())
        errors = [k for k, v in error_lib.items() if not v]
        error_list = self.explain_errors(errors)
        return (b, error_list)

    class AdTypes(models.TextChoices):
        SALE = "S", _("Sale")
        LEASE = "L", _("Lease")

    type = models.CharField(max_length=1, choices=AdTypes.choices, default=AdTypes.SALE, blank=False, null=False)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    @property
    def location(self):
        return self.owner.location

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created", "modified"]


def upload_for_user(instance, filename):
    listing = instance.listing
    return f"{listing.owner.email}/{listing.pk}/{filename}"


class ImageModel(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_for_user)
    thumbnail = ImageSpecField(
        source="image", processors=[ResizeToFill(128, 128)], format="JPEG", options={"quality": 60}
    )
    big_img = ImageSpecField(
        source="image", processors=[ResizeToFill(600, 400)], format="JPEG", options={"quality": 90}
    )

    def __str__(self):
        return self.image.name

    @property
    def name(self):
        return Path(self.image.url).stem


## CAR MODELS
class CarMake(models.Model):
    makeId = models.IntegerField(
        blank=False, choices=cardata.CarMakes.choices, default=cardata.CarMakes.NODATA, primary_key=True
    )
    name = models.CharField(max_length=120, verbose_name="Manufacturer", unique=True, editable=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Manufacturers"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    modelId = models.IntegerField(
        choices=cardata.CarModels.choices, default=cardata.CarModels.NODATA, primary_key=True
    )
    name = models.CharField(max_length=120, verbose_name="model", editable=True)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")

    class Meta:
        ordering = ["make", "name"]
        verbose_name_plural = "Models"

    def __str__(self) -> str:
        return self.name


class CarDetails(models.Model):
    class Transmission(models.TextChoices):
        AUTOMATIC = "AUTO", _("Automatic")
        MANUAL = "MANUAL", _("Manual")
        SEMI = "SEMI", _("Half/Semi-automatic")
        NODATA = "NODATA", _("Unknown")

    class FuelType(models.TextChoices):
        BENZINE = "B", _("Benzine")
        DIESEL = "D", _("Diesel")
        LPG = "L", _("LPG")
        CNG = "C", _("CNG")
        HVB = "2", _("Elektro/Benzine")
        HVD = "3", _("Elektro/Diesel")
        ETHANOL = "M", _("Ethanol")
        ELEKTRISCH = "E", _("Elektrisch")
        HYDRO = "H", _("Waterstof")
        OTHER = "O", _("Overig")

    owning_listing = models.OneToOneField(
        Listing, related_name="cardetails", blank=False, default=None, on_delete=models.CASCADE
    )
    transmission = models.CharField(max_length=6, choices=Transmission.choices, default=Transmission.NODATA)
    fuel_type = models.CharField(max_length=1, choices=FuelType.choices, default=FuelType.OTHER)
    vehicletype = models.CharField(max_length=64, blank=True)
    color = models.CharField(max_length=64, blank=True)
    color_secondary = models.CharField(max_length=64, blank=True)
    num_doors = models.IntegerField(blank=False)
    num_seats = models.IntegerField(blank=False)
    body = models.CharField(max_length=64, blank=True)
    make = models.ForeignKey(CarMake, on_delete=models.SET_DEFAULT, default=0, null=False)
    model = models.ForeignKey(CarModel, on_delete=models.SET_DEFAULT, default=0, null=False)

    def __str__(self) -> str:
        return f"details for {self.owning_listing}"


class PricingModelLease(models.Model):
    class PriceTypeLease(models.TextChoices):
        PRIVATE = "P", _("Private Lease")
        OPERATIONAL = "O", _("Operational Lease")
        FINANCIAL = "F", _("Financial Lease")

    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="price_model_L")
    pricetype = models.CharField(
        max_length=1, choices=PriceTypeLease.choices, blank=False, default=PriceTypeLease.OPERATIONAL
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)

    def __str__(self) -> str:
        return f'{self.price}/{_("Month")}'


class PricingModelBuy(models.Model):
    class PriceTypeBuy(models.TextChoices):
        FIXED = "F", _("Fixed price")
        NEGOTIABLE = "N", _("Negotiable")
        BIDDING = "O", _("Open for bidding")

    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="price_model_S")
    pricetype = models.CharField(max_length=2, choices=PriceTypeBuy.choices, blank=False, default=PriceTypeBuy.FIXED)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)

    def __str__(self) -> str:
        return f"{self.price}"
