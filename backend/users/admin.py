from django.contrib import admin

from . import models


@admin.register(models.CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    list_display = ('email', 'username')


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    list_display = ('user', 'author')
