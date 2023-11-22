from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов"""
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        blank=False)
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        blank=False)
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True,
        blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(
        'Название',
        max_length=200,
        blank=False)
    tags = models.ManyToManyField(
        Tag,
        blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredients',
        verbose_name='Ингредиенты', related_name='recipe')
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
    )
    text = models.TextField(
        'Текстовое описание', blank=False)
    cooking_time = models.PositiveIntegerField(
        'Время приготовления', blank=False,
        validators=[MinValueValidator(1, 'Мин. время - 1 минута')])
    author = models.ForeignKey(
        User, related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        blank=False)
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)


class ShoppingCart(models.Model):
    """Модель списка покупок пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE, related_name='shopping_cart_recipe',
        verbose_name='Покупка')
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        blank=False)

    def __str__(self):
        return f'{self.user} добавил в список покупки {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-created_at',)


class UserFavorite(models.Model):
    """Модель избранного для пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт')
    created_at = models.DateTimeField(
        'Дата создания', auto_now_add=True,
        blank=False)

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-created_at',)


class RecipeIngredients(models.Model):
    """Модель списка ингредиентов для рецепта"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    amount = models.PositiveIntegerField(
        'Количество ингредиентов',
        blank=False,
        validators=[MinValueValidator(
            1, 'Должно быть не менее 1 единицы!')])

    def __str__(self):
        return f'{self.ingredient.name}, {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
