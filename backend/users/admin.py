from django.contrib import admin

from . import models


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    list_display = ('email', 'username')


admin.site.register(models.CustomUser, UserAdmin)
admin.site.register(models.Subscription)
