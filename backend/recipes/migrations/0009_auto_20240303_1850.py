# Generated by Django 3.2.16 on 2024-03-03 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20240229_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ingredient', 'verbose_name_plural': 'Ingredients'},
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredient',
            field=models.ManyToManyField(through='recipes.RecipeIngredient', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(to='recipes.Tag'),
        ),
        migrations.AlterField(
            model_name='shoppingcard',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cards', to='recipes.recipe', verbose_name='Recipe'),
        ),
        migrations.DeleteModel(
            name='TagRecipe',
        ),
    ]