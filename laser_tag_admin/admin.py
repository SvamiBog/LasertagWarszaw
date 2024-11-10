from django.contrib import admin
from django.contrib.auth.models import Group


if admin.site.is_registered(Group):
    admin.site.unregister(Group)
