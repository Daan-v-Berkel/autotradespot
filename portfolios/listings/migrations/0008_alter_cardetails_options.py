# Generated by Django 5.0 on 2024-08-16 02:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0007_remove_listing_viewcount_listingviews"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cardetails",
            name="options",
            field=models.ManyToManyField(blank=True, related_name="options", to="listings.caroption"),
        ),
    ]
