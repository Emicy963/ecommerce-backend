from rest_framework import serializers
from .models import Category, Product


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de produtos.
    Inclui informações básicas e o nome da loja.
    """

    store_name = serializers.CharField(
        source="store.name", read_only=True, help_text="Nome da loja"
    )

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price", "store_name", "in_stock"]


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalhes de produtos.
    Inclui todas as informações do produto.
    """

    store = serializers.StringRelatedField(read_only=True, help_text="Nome da loja")
    category = serializers.StringRelatedField(
        read_only=True, help_text="Nome da categoria"
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "price",
            "store",
            "category",
            "in_stock",
            "stock_quantity",
            "created_at",
        ]


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de categorias.
    Inclui informações básicas da categoria.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalhes de categorias.
    Inclui a lista de produtos da categoria.
    """

    products = ProductListSerializer(
        many=True, read_only=True, help_text="Produtos da categoria"
    )

    class Meta:
        model = Category
        fields = ["id", "name", "image", "products"]


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de produtos.
    Inclui apenas os campos necessários para criação.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "image",
            "featured",
            "in_stock",
            "stock_quantity",
            "category",
        ]

    def create(self, validated_data):
        """
        Cria um novo produto associado à loja do usuário autenticado.
        """
        # Obtém a loja do contexto
        user = self.context["request"].user
        if not hasattr(user, "store"):
            raise serializers.ValidationError("Você não possui uma loja.")

        validated_data["store"] = user.store
        return super().create(validated_data)
