from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Store
from .models import Category, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    """Testes para o modelo Category"""

    def test_create_category(self):
        """Testa a criação de uma categoria"""

        category = Category.objects.create(
            name="Test Category",
        )
        self.assertEqual(category.name, "Test Category")
        self.assertTrue(category.slug) # Verifica se o slug foi gerado automaticamente


class ProductModelTest(TestCase):
    """Testes para o modelo Product"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@example.com",
            password="sellerpass123",
            user_type="seller",
            is_approved_seller=True
        )
        self.store = Store.objects.create(
            name="Test Store",
            description="A test store",
            owner=self.seller
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product",
            price=10.99,
            category=self.category,
            store=self.store,
            featured=True
        )
