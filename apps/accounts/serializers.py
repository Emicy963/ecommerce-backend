from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Store

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo User.
    Utilizado para exibir informações básicas do usuário.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "avatar_url",
            "birth_date",
            "phone",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    Inclui campos de senha e confirmação de senha.
    """

    password = serializers.CharField(write_only=True, help_text="Senha do usuário")
    confirm_password = serializers.CharField(
        write_only=True, help_text="Confirmação da senha"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "user_type",
            "birth_date",
            "phone",
        ]

    def validate(self, attrs):
        """
        Valida se as senhas coincidem.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        """
        Cria um novo usuário com os dados validados.
        """
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Store.
    Inclui informações do proprietário da loja.
    """

    owner = UserSerializer(read_only=True, help_text="Proprietário da loja")

    class Meta:
        model = Store
        fields = ["id", "name", "slug", "description", "logo", "owner", "is_active"]
        read_only_fields = ["slug"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtenção de tokens JWT.
    Permite login com username ou email e adiciona informações do usuário ao token.
    """

    @classmethod
    def get_token(cls, user):
        """
        Adiciona informações personalizadas ao token JWT.
        """
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.get_full_name() or user.username
        token["user_type"] = user.user_type
        return token

    def validate(self, attrs):
        """
        Valida as credenciais do usuário, permitindo login com email ou username.
        """
        identifier = attrs.get("username")
        password = attrs.get("password")

        if identifier and password:
            try:
                user_obj = User.objects.get(email=identifier)
                # Se encontrado por email, define username como email
                attrs["username"] = user_obj.username
            except User.DoesNotExist:
                # Se não encontrado por email, prossegue com username
                pass

        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "name": self.user.get_full_name() or self.user.username,
            "user_type": self.user.user_type,
        }
        return data
