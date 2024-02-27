from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
    MinValueValidator,
)
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=200, validators=[
        MinLengthValidator(1),
        MaxLengthValidator(200)
    ])
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
        ])
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Enter a valid slug in the format.',
                code='invalid_slug_format',
            )]
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(null=True, upload_to='media/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'
