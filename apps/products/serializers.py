from rest_framework import serializers
from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price", "store_name", "in_stock"]
