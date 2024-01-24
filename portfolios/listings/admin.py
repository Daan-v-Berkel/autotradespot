from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.register(Listing)
admin.site.register(CarDetails)
admin.site.register(PricingModelBuy)
admin.site.register(PricingModelLease)
