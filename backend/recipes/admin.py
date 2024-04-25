from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCard, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_display_links = ('name', 'color', 'slug')
    ordering = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ('name', 'measurement_unit')
    ordering = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_display_links = ('recipe', 'ingredient')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'count_favorite',
    )
    list_display_links = ('author', 'name')
    ordering = ('author', 'name')
    list_filter = ('author', 'name', 'tags')

    @admin.display(description='Добавлен в избранное')
    def count_favorite(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_display_links = ('recipe', 'user')


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_display_links = ('recipe', 'user')
