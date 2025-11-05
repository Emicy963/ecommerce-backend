from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Store
from .serializers import (
    CustomTokenObtainPairSerializer,
    StoreSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View personalizada para obtenção de token JWT.
    Utiliza o CustomTokenObtainPairSerializer para adicionar informações
    adicionais ao token.
    """

    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Endpoint para registro de novos usuários.

    Parâmetros:
    - Dados do usuário no corpo da requisição

    Retorna:
    - Mensagem de sucesso ou erros de validação
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "Usuário criado com sucesso."}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Endpoint para logout de usuários.
    Adiciona o token refresh à blacklist para invalidá-lo.

    Parâmetros:
    - refresh_token no corpo da requisição

    Retorna:
    - Mensagem de sucesso ou erro
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {"message": "Logout realizado com sucesso."}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Endpoint para obter o perfil do usuário autenticado.

    Retorna:
    - Dados do usuário
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_store(request):
    """
    Endpoint para criação de uma nova loja.
    Apenas usuários do tipo 'seller' podem criar lojas.

    Parâmetros:
    - Dados da loja no corpo da requisição

    Retorna:
    - Dados da loja criada ou mensagem de erro
    """
    # Verifica se o usuário é um vendedor
    if request.user.user_type != "seller":
        return Response(
            {"error": "Apenas vendedores podem criar lojas"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Verifica se o usuário já possui uma loja
    if hasattr(request.user, "store"):
        return Response(
            {"error": "Você já possui uma loja"}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = StoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def manage_store(request):
    """
    Endpoint para gerenciamento da loja do usuário.
    Permite visualizar e atualizar dados da loja.

    Retorna:
    - Dados da loja ou mensagem de erro
    """
    try:
        store = request.user.store
    except Store.DoesNotExist:
        return Response(
            {"error": "Loja não encontrada"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Views administrativas
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_sellers(request):
    """
    Endpoint para obter lista de vendedores pendentes de aprovação.
    Apenas administradores podem acessar este endpoint.

    Retorna:
    - Lista de vendedores pendentes
    """
    # Verifica se o usuário é um administrador
    if request.user.user_type != "admin":
        return Response({"error": "Permissão negada"}, status=status.HTTP_403_FORBIDDEN)

    pending_sellers = User.objects.filter(user_type="seller", is_approved_seller=False)
    serializer = UserSerializer(pending_sellers, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_seller(request, user_id):
    """
    Endpoint para aprovar um vendedor.
    Apenas administradores podem acessar este endpoint.

    Parâmetros:
    - user_id: ID do vendedor a ser aprovado

    Retorna:
    - Mensagem de sucesso ou erro
    """
    # Verifica se o usuário é um administrador
    if request.user.user_type != "admin":
        return Response({"error": "Permissão negada"}, status=status.HTTP_403_FORBIDDEN)

    try:
        seller = User.objects.get(id=user_id, user_type="seller")
        seller.is_approved_seller = True
        seller.save()

        # Ativa a loja se existir
        if hasattr(seller, "store"):
            seller.store.is_active = True
            seller.store.save()

        return Response({"message": "Vendedor aprovado com sucesso"})
    except User.DoesNotExist:
        return Response(
            {"error": "Vendedor não encontrado"}, status=status.HTTP_404_NOT_FOUND
        )
