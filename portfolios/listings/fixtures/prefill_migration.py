from django.db import migrations
from django.core.management import call_command

def load_inital_carmakes(apps, schema_editor):
    call_command('loaddata', 'listings/car_make_data.json', verbosity=2)


def unload_initial_carmakes(apps, schema_editor):
    Make = apps.get_model('listings', 'CarMake')
    Make.objects.all().delete()

def load_inital_carmodels(apps, schema_editor):
    call_command('loaddata', 'listings/car_model_data.json', verbosity=2)


def unload_initial_carmodels(apps, schema_editor):
    Model = apps.get_model('listings', 'CarModel')
    Model.objects.all().delete()
    
def load_inital_caroptions(apps, schema_editor):
    call_command('loaddata', 'listings/car_options_data.json', verbosity=2)


def unload_initial_caroptions(apps, schema_editor):
    Model = apps.get_model('listings', 'CarOption')
    Model.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_inital_carmakes, unload_initial_carmakes),
        migrations.RunPython(load_inital_carmodels, unload_initial_carmodels),
        migrations.RunPython(load_inital_caroptions, unload_initial_caroptions)
    ]
