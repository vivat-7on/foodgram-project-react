from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator)
from django.db import models


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
        null=True,
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
    pass


class Recipe(models.Model):
    pass
