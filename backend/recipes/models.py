from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
    MinValueValidator,
)
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1), MaxLengthValidator(200)],
        verbose_name='Имя тега'
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
                message='Enter a valid color in HEX format.',
                code='invalid_color_format',
            )
        ],
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Enter a valid slug in the format.',
                code='invalid_slug_format',
            )],
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиет'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, verbose_name='Назнвание рецепта')
    image = models.ImageField(
        null=True,
        upload_to='uploads/',
        default=None,
        blank=True,
        verbose_name='Картинка',

    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Игредиент',
        related_name='recipe_ingredients'
    )
    amount = models.IntegerField(verbose_name='Amount')

    class Meta:
        verbose_name = 'Игредиент для рецепта'
        verbose_name_plural = 'Игредиенты для рецепта'

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorited_by'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.recipe} favorite for {self.user.username}'


class ShoppingCard(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cards'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cards'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списоки покупок'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.recipe} is {self.user.username}\'s card'
