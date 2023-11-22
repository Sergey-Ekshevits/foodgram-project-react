from django.contrib import admin
from django.db.models import Count
from . import models as my_models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'total_favorites')
    list_filter = ('name', 'author', 'tags')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_favorites=Count('favorite_recipe'))
        return queryset

    def total_favorites(self, obj):
        return obj.total_favorites

    total_favorites.short_description = 'Добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(my_models.Recipe, RecipeAdmin)
admin.site.register(my_models.Tag)
admin.site.register(my_models.Ingredient, IngredientAdmin)
admin.site.register(my_models.RecipeIngredients)
admin.site.register(my_models.ShoppingCart)
admin.site.register(my_models.UserFavorite)
