from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    """Testes para o modelo CustomUser."""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "buyer"
        }
    
    def test_create_user(self):
        """Testa a criação de um usuário comum"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.user_type, self.user_data["user_type"])
        self.assertTrue(user.check_password(self.user_data["password"]))
    
    def test_create_superuser(self):
        """Testa a criação de um superusuário"""
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        self.assertEqual(admin_user.username, "admin")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
