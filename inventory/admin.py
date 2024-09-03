from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from inventory.models import User, EbayItem

admin.site.register(User, UserAdmin)
admin.site.register(EbayItem)
