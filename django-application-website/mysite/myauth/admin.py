from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "user", "city", "date_of_birth", "avatar"
    fieldsets = [
        (None, {
            "fields": ("user", "city", "date_of_birth", "avatar"),
        }),
    ]
