from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.orders.models import OrderItem
from .models import ProductRating, Review
from .serializers import ProductRatingSerializer, ReviewSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review(request):
    """
    Adicionar uma avaliação para um produto.

    Args:
        request: Objeto de requisição contendo os dados da avaliação

    Returns:
        Response: Dados da avaliação criada ou mensagem de erro
    """
    product_id = request.data.get("product_id")
    rating = request.data.get("rating")
    comment = request.data.get("comment")

    if not product_id or not rating:
        return Response(
            {"error": "É necessário o ID do produto e o rating"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        from apps.products.models import Product

        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )

    # Verificar se o usuário já avaliou este produto
    if Review.objects.filter(product=product, user=request.user).exists():
        return Response(
            {"error": "Você já avaliou este produto."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verificar se o usuário comprou este produto
    has_purchased = OrderItem.objects.filter(
        product=product,
        order__user=request.user,
        order__status__in=["confirmed", "processing", "shipped", "delivered"],
    ).exists()

    if not has_purchased:
        return Response(
            {"error": "Podes apenas avaliar o produto que já comprou."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Criar avaliação
    review = Review.objects.create(
        product=product, user=request.user, rating=rating, comment=comment
    )

    serializer = ReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    """
    Atualiza uma avaliação existente.

    Args:
        request: Objeto de requisição contendo os dados atualizados
        pk: ID da avaliação a ser atualizada

    Returns:
        Response: Dados da avaliação atualizada ou mensagem de erro
    """
    try:
        review = Review.objects.get(pk=pk, user=request.user)
    except Review.DoesNotExist:
        return Response(
            {"error": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND
        )

    rating = request.data.get("rating")
    comment = request.data.get("comment")

    if rating:
        review.rating = rating
    if comment:
        review.comment = comment

    review.save()

    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    """
    Exclui uma avaliação.

    Args:
        request: Objeto de requisição
        pk: ID da avaliação a ser excluída

    Returns:
        Response: Mensagem de sucesso ou erro
    """
    try:
        review = Review.objects.get(pk=pk, user=request.user)
        review.delete()
        return Response(
            {"message": "Avaliação excluída com sucesso."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_product_reviews(request, product_id):
    """
    Obtém todas as avaliações para um produto específico.

    Args:
        request: Objeto de requisição
        product_id: ID do produto

    Returns:
        Response: Lista de avaliações e classificação média ou mensagem de erro
    """
    try:
        from apps.products.models import Product

        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Produto não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )

    reviews = Review.objects.filter(product=product)
    serializer = ReviewSerializer(reviews, many=True)

    # Obter classificação média
    try:
        rating = ProductRating.objects.get(product=product)
        rating_data = ProductRatingSerializer(rating).data
    except ProductRating.DoesNotExist:
        rating_data = {"average_rating": 0.0, "total_reviews": 0}

    return Response({"reviews": serializer.data, "rating": rating_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_reviews(request):
    """
    Obtém todas as avaliações do usuário.

    Args:
        request: Objeto de requisição

    Returns:
        Response: Lista de avaliações do usuário
    """
    reviews = Review.objects.filter(user=request.user)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# Views para vendedores
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_store_product_reviews(request):
    """
    Obtém todas as avaliações dos produtos da loja do vendedor.

    Args:
        request: Objeto de requisição

    Returns:
        Response: Lista de avaliações dos produtos da loja ou mensagem de erro
    """
    # Verificar se o usuário é um vendedor
    if request.user.user_type != "seller":
        return Response(
            {"error": "Apenas vendedores podem acessar esta informação."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Verificar se o vendedor tem uma loja
    if not hasattr(request.user, "store"):
        return Response(
            {"error": "Você não tem uma loja associada."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Obter avaliações dos produtos da loja
    store_products = request.user.store.products.all()
    reviews = Review.objects.filter(product__in=store_products)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
