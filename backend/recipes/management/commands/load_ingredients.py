import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default=None,
            help='Путь до CSV-файла с ингредиентами '
                 '(столбцы: название, единица измерения)',
        )

    def handle(self, *args, **options):
        path = options['path'] or self.default_path()
        try:
            with open(path, encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                ingredients = [
                    Ingredient(name=row[0], measurement_unit=row[1])
                    for row in reader
                    if len(row) >= 2
                ]
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {path}')

        Ingredient.objects.bulk_create(
            ingredients, batch_size=1000, ignore_conflicts=True
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортировано ингредиентов: {len(ingredients)}'
            )
        )

    def default_path(self):
        candidates = [
            os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv'),
            os.path.join(
                os.path.dirname(settings.BASE_DIR), 'data', 'ingredients.csv'
            ),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]
