from django.contrib import admin
from .models import Bench, TimeSlot, Booking

admin.site.register(Bench)
admin.site.register(TimeSlot)
admin.site.register(Booking)