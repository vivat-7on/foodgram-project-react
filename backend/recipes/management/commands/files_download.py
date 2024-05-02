import json
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def handle(self, *args, **options):
        directory_path = os.path.normpath(
            os.path.join(settings.BASE_DIR, '..', 'data'))
        file_path = os.path.join(directory_path, 'ingredients.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                for kwargs in file_data:
                    try:
                        Ingredient.objects.create(**kwargs)
                    except ValidationError as e:
                        self.stderr.write(self.style.ERROR(
                            f'Error creating ingredient: {e}'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('File not found'))
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e}'))
        else:
            self.stdout.write(
                self.style.SUCCESS('Successfully loaded ingredients'))
