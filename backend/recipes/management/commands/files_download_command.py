import os
import csv, json

from django.core.management import BaseCommand


from backend import settings
# from recipes.models import Ingredient


# from backend.recipes.models import Ingredient


class Command(BaseCommand):
    pass


directory_path = os.path.normpath(os.path.join(settings.BASE_DIR, '..', 'data'))
# files = os.listdir(directory_path)


with open(directory_path + '/ingredients.json', 'r', encoding='utf-8') as f:
    file = json.load(f)
    print(file)
    # for kwargs in file:
    #     Ingredient.objects.create(**kwargs)
