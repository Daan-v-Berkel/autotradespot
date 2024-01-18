# Generated by Django 5.0 on 2024-01-15 12:22

import django.db.models.deletion
import django.utils.timezone
import portfolios.listings.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CarMake",
            fields=[
                ("makeId", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "name",
                    models.CharField(
                        max_length=120, unique=True, verbose_name="Manufacturer"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Manufacturers",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CarOption",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="CarModel",
            fields=[
                ("modelId", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, verbose_name="model")),
                (
                    "make",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="models",
                        to="listings.carmake",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Models",
                "ordering": ["make", "name"],
            },
        ),
        migrations.CreateModel(
            name="Listing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, max_length=3000)),
                ("available_from", models.DateField(default=django.utils.timezone.now)),
                ("viewcount", models.IntegerField(default=0)),
                ("created", models.DateField(editable=False)),
                ("modified", models.DateField()),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Inactive"),
                            (1, "Active"),
                            (2, "Draft"),
                            (3, "Reserved"),
                            (4, "Sold"),
                            (5, "Removed"),
                            (6, "Reported"),
                        ],
                        default=2,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("S", "Sale"), ("L", "Lease")],
                        default="S",
                        max_length=1,
                    ),
                ),
                (
                    "favourites_list",
                    models.ManyToManyField(
                        blank=True,
                        default=None,
                        related_name="favourites_list",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created", "modified"],
            },
        ),
        migrations.CreateModel(
            name="ImageModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to=portfolios.listings.models.upload_for_user
                    ),
                ),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="listings.listing",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CarDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transmission",
                    models.CharField(
                        choices=[
                            ("AUTO", "Automatic"),
                            ("MANUAL", "Manual"),
                            ("SEMI", "Half/Semi-automatic"),
                        ],
                        default="MANUAL",
                        max_length=6,
                    ),
                ),
                (
                    "fuel_type",
                    models.CharField(
                        choices=[
                            ("B", "Benzine"),
                            ("D", "Diesel"),
                            ("L", "LPG"),
                            ("C", "CNG"),
                            ("2", "Elektro/Benzine"),
                            ("3", "Elektro/Diesel"),
                            ("M", "Ethanol"),
                            ("E", "Elektrisch"),
                            ("H", "Waterstof"),
                            ("O", "Overig"),
                        ],
                        default="O",
                        max_length=1,
                    ),
                ),
                ("color", models.CharField(blank=True, max_length=64)),
                ("color_interior", models.CharField(blank=True, max_length=64)),
                ("num_doors", models.IntegerField(blank=True)),
                ("num_seats", models.IntegerField(blank=True)),
                ("variant", models.CharField(blank=True, max_length=64)),
                ("manufacture_date", models.DateField(blank=True)),
                ("mileage", models.IntegerField()),
                (
                    "make",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="listings.carmake",
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="listings.carmodel",
                    ),
                ),
                (
                    "options",
                    models.ManyToManyField(
                        blank=True, related_name="options", to="listings.caroption"
                    ),
                ),
                (
                    "owning_listing",
                    models.OneToOneField(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cardetails",
                        to="listings.listing",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PricingModelBuy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "pricetype",
                    models.CharField(
                        choices=[
                            ("F", "Fixed price"),
                            ("N", "Negotiable"),
                            ("O", "Open for bidding"),
                        ],
                        default="F",
                        max_length=2,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "listing",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_model_S",
                        to="listings.listing",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PricingModelLease",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "pricetype",
                    models.CharField(
                        choices=[
                            ("P", "Private"),
                            ("O", "Operational"),
                            ("NO", "Netto Operational"),
                            ("F", "Financial"),
                            ("S", "Short"),
                        ],
                        default="O",
                        max_length=2,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "listing",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_model_L",
                        to="listings.listing",
                    ),
                ),
            ],
        ),
    ]
