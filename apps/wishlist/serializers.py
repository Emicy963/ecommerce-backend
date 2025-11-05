from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wishlist
from apps.products.serializers import ProductListSerializer

User = get_user_model()


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer para itens da lista de desejos.
    """

    user = serializers.StringRelatedField(
        read_only=True, help_text="Usuário dono da lista de desejos"
    )
    product = ProductListSerializer(
        read_only=True, help_text="Produto na lista de desejos"
    )

    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "created_at"]
