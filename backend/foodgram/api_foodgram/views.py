from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from users.models import Subscription

from .filters import RecipeFilter
from .models import (Ingredient, Recipe, RecipeIngredients, ShoppingCart, Tag,
                     UserFavorite)
from .permissions import IsAuthorOrReadPermission, IsAuthorPermission
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeReadSerializer, RecipeResponseSerializer,
                          SubscriptionSerializer, TagSerializer)
from django.conf import settings

User = get_user_model()


class TagView(mixins.RetrieveModelMixin,
              mixins.ListModelMixin,
              GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientView(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [filters.SearchFilter, ]
    search_fields = ('^name',)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadPermission,
                          permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query = super().get_queryset()
        is_favorited = self.request.query_params.get(
            'is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None)
        if is_favorited == '1' and self.request.user.is_authenticated:
            query = Recipe.objects.filter(
                favorite_recipe__user=self.request.user)
        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            query = Recipe.objects.filter(
                shopping_cart_recipe__user=self.request.user)
        return query

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeResponseSerializer
        return super().get_serializer_class()

    def _handle_cart_or_favorite(self, request, pk, model, serializer_class):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response({'errors': 'Рецепт не найден'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(recipe)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response({"error": "Уже существует"},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт не найден'},
                    status=status.HTTP_404_NOT_FOUND)
            item = model.objects.filter(user=user,
                                        recipe=recipe)
            if item:
                item.delete()
                return Response(
                    {"detail": "Удалено"},
                    status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Некорректные данные"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            serializer_class=RecipeReadSerializer)
    def shopping_cart(self, request, pk):
        return self._handle_cart_or_favorite(
            request,
            pk,
            ShoppingCart,
            RecipeReadSerializer)

    @action(detail=True, methods=['POST', 'DELETE'],
            serializer_class=RecipeReadSerializer)
    def favorite(self, request, pk):
        return self._handle_cart_or_favorite(
            request,
            pk,
            UserFavorite,
            RecipeReadSerializer)

    @action(detail=False, methods=['GET'],
            serializer_class=None,
            permission_classes=[permissions.IsAuthenticated, ])
    def download_shopping_cart(self, request):
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=Shopping.pdf'

        p = canvas.Canvas(response)

        user_cart = (ShoppingCart.
                     objects.filter(user=self.request.user).
                     select_related('recipe'))
        recipes_in_cart = [cart_item.recipe for cart_item in user_cart]

        all_ingredients = (RecipeIngredients.
                           objects.filter(recipe__in=recipes_in_cart).
                           select_related('ingredient'))
        ingredients_list = {}

        for recipe_ingredient in all_ingredients:
            name = recipe_ingredient.ingredient.name
            amount = recipe_ingredient.amount
            measurement_unit = recipe_ingredient.ingredient.measurement_unit
            if name not in ingredients_list:
                ingredients_list[name] = {
                    'amount': amount,
                    'measure': measurement_unit}
            else:
                ingredients_list[name]['amount'] += amount
        font_path = getattr(settings, 'FONT_PATH', None)
        pdfmetrics.registerFont(TTFont('Arial', str(font_path) + '/arial.ttf'))
        p.setFont("Arial", 12)
        p.drawCentredString(300, 750, "Список покупок")
        y_coordinate = 700
        for ingredient, detail in ingredients_list.items():
            ingredient_text = (f"-{ingredient}: "
                               f"{detail['amount']} "
                               f"{detail['measure']}")
            p.drawString(100, y_coordinate, ingredient_text)
            y_coordinate -= 20
        p.showPage()
        p.save()
        return response


class SubscriptionListView(mixins.ListModelMixin, GenericViewSet):
    serializer_class = SubscriptionSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthorPermission, ]

    def get_queryset(self):
        current_user = self.request.user
        following = current_user.subscriber.all()
        subscribed_users = [subscription.author for subscription in following]
        return subscribed_users


#
class SubscriptionCreateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, id):
        current_user = request.user
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {'errors': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND)
        context = {'request': request}
        serializer = SubscriptionSerializer(
            author,
            data=request.data,
            context=context)
        if serializer.is_valid():
            if author == current_user:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=current_user,
                                           author=author).exists():
                return Response(
                    {'errors': 'Подписка уже существует'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscription(user=current_user, author=author)
            subscription.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        current_user = request.user
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(
                {'errors': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND)
        subscription = Subscription.objects.filter(user=current_user,
                                                   author=author)
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Некорректные данные'},
                        status=status.HTTP_400_BAD_REQUEST)
