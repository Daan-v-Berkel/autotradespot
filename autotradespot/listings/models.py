from datetime import datetime, timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from autotradespot.listings.tasks import send_review_mail_task

User = get_user_model()


# For complicated queries with filters
class ListingQuerySet(models.QuerySet):
    def search(self, searchdict={}):
        qs = self.filter(status__exact=self.model.Status.ACTIVE)
        if searchdict.get("listing_type", []):
            qs = qs.filter(type__exact=searchdict["listing_type"])
        if searchdict.get("fuel_type", []):
            qs = qs.filter(cardetails__fuel_type__in=searchdict["fuel_type"])
        if searchdict.get("transmission", []):
            qs = qs.filter(cardetails__transmission__in=searchdict["transmission"])
        if searchdict.get("num_doors", []):
            qs = qs.filter(cardetails__num_doors__in=searchdict["num_doors"])
        if searchdict.get("make", []):
            qs = qs.filter(cardetails__make__exact=searchdict["make"])
        if searchdict.get("model", []):
            qs = qs.filter(cardetails__model__exact=searchdict["model"])
        if searchdict["listing_type"] == "S":
            if searchdict.get("type", []):
                qs = qs.filter(price_model_S__pricetype__exact=searchdict["type"])
            if searchdict.get("from_price_sale", []):
                qs = qs.filter(price_model_S__price__gte=searchdict["from_price_sale"])
            if searchdict.get("to_price_sale", []):
                qs = qs.filter(price_model_S__price__lte=searchdict["to_price_sale"])
            if searchdict.get("max_kms_driven", []):
                qs = qs.filter(cardetails__mileage__lte=searchdict["max_kms_driven"])
        elif searchdict["listing_type"] == "L":
            if searchdict.get("type", []):
                qs = qs.filter(price_model_L__pricetype__exact=searchdict["type"])
            if searchdict.get("from_price_lease", []):
                qs = qs.filter(price_model_L__price__gte=searchdict["from_price_lease"])
            if searchdict.get("to_price_lease", []):
                qs = qs.filter(price_model_L__price__lte=searchdict["to_price_lease"])
            if searchdict.get("min_monthly_kms", []):
                qs = qs.filter(price_model_L__annual_kms__gte=searchdict["min_monthly_kms"])
            if int(searchdict.get("lease_period", [])):
                qs = qs.filter(
                    price_model_L__lease_period__gte=datetime.now()
                    + timedelta(days=int(searchdict["lease_period"]) * 30),
                    price_model_L__lease_period__lte=datetime.now()
                    + timedelta(days=int(searchdict["lease_period"]) * 30 + 356),
                )

        return qs


class Listing(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=3000, blank=True)
    available_from = models.DateField(default=timezone.now)
    favourites_list = models.ManyToManyField(User, related_name="favourites_list", blank=True, default=None)

    objects = ListingQuerySet.as_manager()

    def increment_views(self):
        view, created = ListingViews.objects.get_or_create(listing=self, user=self.owner)
        view.save()

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
        UNDER_REVIEW = 7, _("under review")

    status = models.IntegerField(choices=Status.choices, default=Status.DRAFT)

    @property
    def status_name(self):
        return self.Status.choices[self.status][1]

    def explain_errors(self, errors):
        if not errors:
            return ""
        error_lib = {
            "status": _(f"this listing hs been {self.status_name} and cannot be changed at this time."),
            "pricing": _(
                "this listing has no pricing details, these are needed before being able to activate the listing."
            ),
            "images": ("this listing has either no images, or the images do not meet the minimum requirements"),
            "details": ("this listing has insufficient details about the listed object"),
        }
        return [str(v) for k, v in error_lib.items() if k in errors]

    @property
    def complete_for_posting(self):
        pricing_types = {"S": "price_model_S", "L": "price_model_L"}
        error_lib = {
            "status": self.status not in [5, 6],
            "pricing": getattr(self, pricing_types[self.type], None) is not None,
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

    def set_deleted(self, *args, **kwargs):
        self.status = self.Status.REMOVED
        self.save()

    def set_under_review(self, *args, **kwargs):
        self.status = self.Status.UNDER_REVIEW
        self.save()
        send_review_mail_task(self)

    def set_active(self, *args, **kwargs):
        self.status = self.Status.ACTIVE
        self.save()

    def format(self):
        return _("for sale") if self.type == "S" else _("lease")

    def pricetype(self):
        return getattr(self, f"price_model_{self.type}")

    @property
    def priceform(self):
        m = self.pricetype()
        t = m.get_pricetype_display()
        return t

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def delete_permanent(self):
        image_files = self.imagemodel_set.all()
        for image in image_files:
            image.delete()
        self.delete()

    def visible_to_public(self):
        return self.status in [self.Status.ACTIVE, self.Status.RESERVED, self.Status.SOLD]

    def get_absolute_url(self) -> str:
        return reverse("listings:viewlisting", args=(self.pk,))

    def __str__(self):
        return f"{self.owner}/{self.pk}/{self.title}"

    class Meta:
        ordering = ["created", "modified"]


def upload_for_user(instance, filename):
    listing = instance.listing
    return f"{listing.owner.pk}/{listing.pk}/{filename}"


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


class ListingViews(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_viewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"listing viewed by {self.user.username}"


# CAR MODELS
class CarMake(models.Model):
    makeId = models.IntegerField(blank=False, primary_key=True)
    name = models.CharField(max_length=120, verbose_name="Manufacturer", unique=True, editable=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Manufacturers"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    modelId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120, verbose_name="model", editable=True)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")

    class Meta:
        ordering = ["make", "name"]
        verbose_name_plural = "Models"

    def __str__(self) -> str:
        return self.name


class CarOption(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name


class CarDetails(models.Model):
    class Transmission(models.TextChoices):
        AUTOMATIC = "AUTO", _("Automatic")
        MANUAL = "MANUAL", _("Manual")
        SEMI = "SEMI", _("Half/Semi-automatic")

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

    class BodyType(models.TextChoices):
        COMPACT = "C", _("Compact")
        CONVERTABLE = "CO", _("Convertible")
        COUPE = "COU", _("Coupe")
        SUV = "SUV", _("SUV")
        STATION_WAGON = "SW", _("Station wagon")
        SEDAN = "S", _("Sedan")
        VAN = "V", _("Van")
        TRANSPORTER = "T", _("Transporter")
        OTHER = "O", _("Overig")

    class Condition(models.TextChoices):
        NEW = "N", _("New")
        USED = "U", _("Used")
        CLASSIC = "C", _("Classic")

    def manufacture_years():
        return [(i, i) for i in reversed(range(1950, datetime.now().year))]

    owning_listing = models.OneToOneField(
        Listing, related_name="cardetails", blank=False, default=None, on_delete=models.CASCADE
    )
    transmission = models.CharField(max_length=6, choices=Transmission.choices, default=Transmission.MANUAL)
    fuel_type = models.CharField(max_length=1, choices=FuelType.choices, default=FuelType.BENZINE)
    color = models.CharField(max_length=64, blank=True, null=True)
    color_interior = models.CharField(max_length=64, blank=True, null=True)
    num_doors = models.IntegerField(blank=True, null=True)
    num_seats = models.IntegerField(blank=True, null=True)
    make = models.ForeignKey(CarMake, on_delete=models.SET_DEFAULT, default=0, null=False)
    model = models.ForeignKey(CarModel, on_delete=models.SET_DEFAULT, default=0, null=False)
    variant = models.CharField(max_length=64, blank=True, null=True)
    manufacture_year = models.IntegerField(blank=False, choices=manufacture_years)
    mileage = models.IntegerField(blank=False)
    body_type = models.CharField(max_length=3, choices=BodyType.choices, default=BodyType.COMPACT)
    condition = models.CharField(max_length=1, choices=Condition.choices, default=Condition.USED)
    options = models.ManyToManyField(CarOption, related_name="options", blank=True)

    def __str__(self) -> str:
        return f"details for {self.owning_listing}"

    def full_make_name(self):
        return f"{self.make} {self.model} {self.variant}"

    def appropriate_details(self):
        if self.owning_listing.type == "S":
            miles = f"{self.mileage} kms"
        else:
            miles = f"{self.owning_listing.pricetype().annual_kms} km/y"
        return [self.get_transmission_display(), self.get_fuel_type_display(), miles]

    def full_details(self):
        if self.owning_listing.type == "S":
            miles = (_("mileage"), f"{self.mileage} kms")
        else:
            miles = (_("max km/year"), (f"{self.owning_listing.pricetype().annual_kms} km/y"))
        return [
            (_("fuel"), self.get_fuel_type_display()),
            (_("transmission"), self.get_transmission_display()),
            (_("manufacture year"), self.manufacture_year),
            miles,
            (_("price"), f"€ {self.owning_listing.pricetype()}.-"),
        ]


class PricingModelLease(models.Model):
    class PriceTypeLease(models.TextChoices):
        PRIVATE = "P", _("Private")
        OPERATIONAL = "O", _("Operational")
        NETTOOPERATIONAL = "NO", _("Netto Operational")
        FINANCIAL = "F", _("Financial")
        SHORT = "S", _("Short")

    ANNUAL_KMS = [
        (5000, 5000),
        (7500, 7500),
        (10000, 10000),
        (12000, 12000),
        (15000, 15000),
        (20000, 20000),
        (25000, 25000),
        (30000, 30000),
        (35000, 35000),
        (40000, 40000),
    ]

    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="price_model_L")
    pricetype = models.CharField(
        max_length=2, choices=PriceTypeLease.choices, blank=False, default=PriceTypeLease.OPERATIONAL
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
    annual_kms = models.IntegerField(blank=False, choices=ANNUAL_KMS)
    lease_company = models.CharField(max_length=255, blank=False, null=False)
    lease_period = models.DateField(blank=False, null=False)

    def __str__(self) -> str:
        return f'{self.price.to_integral_value()}/{_("Month")}'


class PricingModelBuy(models.Model):
    class PriceTypeBuy(models.TextChoices):
        FIXED = "F", _("Fixed price")
        NEGOTIABLE = "N", _("Negotiable")
        BIDDING = "O", _("Open for bidding")

    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="price_model_S")
    pricetype = models.CharField(max_length=2, choices=PriceTypeBuy.choices, blank=False, default=PriceTypeBuy.FIXED)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)

    def __str__(self) -> str:
        return f"{self.price.to_integral_value()}"
