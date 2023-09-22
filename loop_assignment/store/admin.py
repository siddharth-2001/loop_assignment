from django.contrib import admin
from.models import Store, StoreStatus, BusinessHours, Timezone
# Register your models here.

admin.site.register([Store, StoreStatus, BusinessHours, Timezone])