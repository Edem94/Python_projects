from rest_framework import serializers
from .models import Product
from .models import Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "created_by",
            "archived",
            "preview1",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
            "receipt",
        )
