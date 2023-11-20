import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer

from .models import (Ingredient, Recipe, RecipeIngredients, ShoppingCart, Tag,
                     UserFavorite)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeUserSerializer(CustomUserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug')
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsRecipeCreateSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(
        required=True, min_value=1)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')
    name = serializers.StringRelatedField(
        source='ingredient.name')
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit')


class IngredientRecipeResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time')
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time')


class RecipeBaseSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True)
    author = RecipeUserSerializer(
        default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeResponseSerializer(
        source='recipe_ingredients', many=True, required=True)
    is_favorited = serializers.SerializerMethodField(
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True)

    def _object_exists(self, instance, target_model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return target_model.objects.filter(
            user=request.user,
            recipe=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        return self._object_exists(instance, ShoppingCart)

    def get_is_favorited(self, instance):
        return self._object_exists(instance, UserFavorite)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart')


class RecipeCreateUpdateSerializer(RecipeBaseSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientsRecipeCreateSerializer(
        source='recipe_ingredients', many=True, required=True)

    def create(self, validated_data):
        ingredients_list = validated_data.pop('recipe_ingredients')
        tags_list = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data)
        print(ingredients_list)
        for item in ingredients_list:
            recipe_ingredients = RecipeIngredients(
                **item, recipe=recipe)
            recipe_ingredients.save()
        for tag in tags_list:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        ingredients_list = validated_data.get('recipe_ingredients')
        tags_list = validated_data.get('tags')
        if not tags_list or not ingredients_list:
            raise ValidationError(
                'Все поля должны быть заполнены'
            )
        instance.ingredients.clear()
        instance.tags.clear()
        for item in ingredients_list:
            recipe_ingredients = RecipeIngredients(
                **item, recipe=instance)
            recipe_ingredients.save()
        for tag in tags_list:
            instance.tags.add(tag)
        instance.save()
        return instance

    def validate_ingredients(self, value):
        items_list = []
        for item in value:
            if item.get('ingredient') in items_list:
                raise ValidationError(
                    'Нельзя добавить 2 одинаковых ингредиента'
                )
            items_list.append(item.get('ingredient'))
        if not items_list:
            raise ValidationError(
                'Список рецептов не может быть пустым'
            )
        return value

    def validate_tags(self, value):
        items_list = []
        for item in value:
            if item in items_list:
                raise ValidationError(
                    'Нельзя добавить 2 одинаковых тэга'
                )
            items_list.append(item)
        if not items_list:
            raise ValidationError(
                'Должен быть хотя бы один тэг'
            )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        instance_tags = instance.tags.all()
        tags = TagSerializer(instance_tags, many=True)
        representation['tags'] = tags.data
        return representation


class RecipeResponseSerializer(RecipeBaseSerializer):
    pass


class UserFavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all())

    class Meta:
        model = UserFavorite
        fields = (
            'id',
            'image',
            'name',
            'cooking_time')
        read_only_fields = (
            'id',
            'image',
            'name',
            'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(
        read_only=True)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', None)
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        output = Recipe.objects.filter(
            author=obj)[:recipes_limit]
        return RecipeReadSerializer(
            output, many=True, read_only=True).data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'is_subscribed',
            'recipes_count')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'is_subscribed',
            'recipes_count')
