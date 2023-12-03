from django.contrib import admin
from django.db.models import Count

from .models import (Recipe,
                     Tag,
                     RecipeIngredients,
                     Ingredient,
                     ShoppingCart,
                     UserFavorite)


@admin.register(Recipe)
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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(RecipeIngredients)
admin.site.register(ShoppingCart)
admin.site.register(UserFavorite)
