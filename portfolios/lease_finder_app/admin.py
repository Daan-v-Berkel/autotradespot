from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.register(Advertisement)
admin.site.register(UserCustomisation)
