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
        verbose_name='Name'
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
        verbose_name='Color'
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
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Measurement Unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    name = models.CharField(max_length=200, verbose_name='Name')
    image = models.ImageField(
        null=True,
        upload_to='uploads/',
        default=None,
        blank=True,
        verbose_name='Image'
    )
    text = models.TextField(verbose_name='Text')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cooking Time'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    amount = models.IntegerField(verbose_name='Amount')

    class Meta:
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Tag',
        related_name='tagged_recipes'
    )

    class Meta:
        verbose_name = 'Tag Recipe'
        verbose_name_plural = 'Tag Recipes'
        unique_together = ('recipe', 'tag')

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='favorited_by'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.recipe} favorite for {self.user.username}'


class ShoppingCard(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='shopping_cards'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='shopping_cards'
    )

    class Meta:
        verbose_name = 'Shopping Card'
        verbose_name_plural = 'Shopping Cards'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.recipe} is {self.user.username}\'s card'
