from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wishlist
from .serializers import WishlistSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    """
    Adiciona ou remove um produto da lista de desejos.

    Args:
        request: Objeto de requisição contendo o ID do produto

    Returns:
        Response: Dados do item adicionado ou mensagem de remoção
    """
    product_id = request.data.get("product_id")

    if not product_id:
        return Response(
            {"error": "ID do produto não fornecido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from apps.products.models import Product

        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )

    user = request.user

    # Verificar se o produto já está na lista de desejos
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        # Se já existe, remover da lista
        wishlist_item.delete()
        return Response(
            {"message": "O produto foi removido da lista de desejos."},
            status=status.HTTP_204_NO_CONTENT,
        )

    # Se não existe, adicionar à lista
    serializer = WishlistSerializer(wishlist_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_wishlist(request):
    """
    Obtém a lista de desejos do usuário.

    Args:
        request: Objeto de requisição

    Returns:
        Response: Lista de itens na lista de desejos do usuário
    """
    wishlist_items = Wishlist.objects.filter(user=request.user)
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_wishlist_item(request, pk):
    """
    Remove um item da lista de desejos.

    Args:
        request: Objeto de requisição
        pk: ID do item a ser removido

    Returns:
        Response: Mensagem de sucesso ou erro
    """
    try:
        wishlist_item = Wishlist.objects.get(pk=pk, user=request.user)
        wishlist_item.delete()
        return Response(
            {"message": "O item foi removido da lista de desejos."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Wishlist.DoesNotExist:
        return Response(
            {"error": "Item não encontrado na lista de desejos."},
            status=status.HTTP_404_NOT_FOUND,
        )
