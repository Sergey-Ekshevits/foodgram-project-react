import csv

from django.core.management.base import BaseCommand
from api_foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла в БД'

    def handle(self, *args, **options):
        with open(
                'data/ingredients_load.csv', 'r',
                encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                ingredients = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'])
                ingredients.save()
            self.stdout.write(self.style.SUCCESS(
                'ingredients.csv загружен в базу данных'))
