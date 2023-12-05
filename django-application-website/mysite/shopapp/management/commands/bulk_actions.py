from django.core.management import BaseCommand
from typing import Sequence
from shopapp.models import Product
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Start demo bulk actions")

        result = Product.objects.filter(name__contains="Smartphone",).update(discount=10)
        print(result)

        self.stdout.write("Done")
