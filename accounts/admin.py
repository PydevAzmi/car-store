from django.contrib import admin

from .models import Location, Profile, User

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Location)
