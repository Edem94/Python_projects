from csv import DictReader
from io import TextIOWrapper
from django.contrib.auth.models import User
from .models import Product, Order


def save_csv_products(file, encoding):
    csv_files = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_files)
    products = [
        Product(**row) for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_files = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_files)
    # orders = []
    # for row in reader:
    #     user_id = int(row['user'])
    #     user = User.objects.get(pk=user_id)
    #     row['user'] = user
    #     orders.append(Order(**row))
    orders = [
        Order(**row) for row in reader
    ]

    Order.objects.bulk_create(orders)
    return orders
