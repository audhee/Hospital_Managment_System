from django.contrib import admin

# Register your models here.
from .models import User, Doctor, Appointment

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Appointment)