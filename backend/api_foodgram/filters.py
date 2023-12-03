from django_filters import rest_framework as filters

from .models import Recipe

CHOICES = (
    (0, 'False'),
    (1, 'True'),
)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES, method='get_favorited')
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES, method='get_shopping_cart')

    def get_favorited(self, queryset, field_name, value):
        if value == '1':
            return queryset.filter(
                favorite_recipe__user=self.request.user)
        else:
            return queryset.all()

    def get_shopping_cart(self, queryset, field_name, value):
        if value == '1':
            return queryset.filter(
                shopping_cart_recipe__user=self.request.user)
        else:
            return queryset.all()

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
