"""
Script para preparar dados de teste no banco de dados
Execute da RAIZ do projeto: python setup_test_data.py
OU: python manage.py shell < setup_test_data.py
"""

import os
import sys

# Detectar se estamos executando via manage.py shell ou diretamente
if "django" not in sys.modules:
    # Adicionar o diretório atual ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Configurar Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")

    import django

    django.setup()

# Agora podemos importar os models
from apps.accounts.models import CustomUser, Store
from apps.products.models import Category, Product


def create_test_data():
    print("\n" + "=" * 60)
    print("🔧 CONFIGURANDO DADOS DE TESTE")
    print("=" * 60 + "\n")

    # 1. Criar categorias
    print("📂 Criando categorias...")
    categories_data = [
        {"name": "Eletrônicos"},
        {"name": "Roupas"},
        {"name": "Livros"},
        {"name": "Móveis"},
    ]

    created_categories = []
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data["name"], defaults=cat_data
        )
        created_categories.append(cat)
        status = "✅ Criado" if created else "ℹ️  Já existe"
        print(f"  {status}: {cat.name}")

    # 2. Criar vendedor aprovado com loja
    print("\n👤 Criando vendedor aprovado...")
    seller, created = CustomUser.objects.get_or_create(
        username="vendedor_aprovado",
        defaults={
            "email": "vendedor@teste.com",
            "first_name": "Vendedor",
            "last_name": "Aprovado",
            "user_type": "seller",
            "is_approved_seller": True,
        },
    )
    if created:
        seller.set_password("Test@123")
        seller.save()
        print("  ✅ Vendedor criado")
    else:
        # Garantir que está aprovado
        if not seller.is_approved_seller:
            seller.is_approved_seller = True
            seller.save()
            print("  ✅ Vendedor aprovado")
        else:
            print("  ℹ️  Vendedor já existe e está aprovado")

    # 3. Criar loja
    print("\n🏪 Criando loja...")
    store, created = Store.objects.get_or_create(
        owner=seller,
        defaults={
            "name": "Loja Tech Angola",
            "description": "Tecnologia e eletrônicos",
            "is_active": True,
        },
    )
    if not store.is_active:
        store.is_active = True
        store.save()
        print("  ✅ Loja ativada")
    status = "✅ Criada" if created else "ℹ️  Já existe"
    print(f"  {status}: {store.name}")

    # 4. Criar produtos
    print("\n📦 Criando produtos...")
    products_data = [
        {
            "name": "Smartphone Samsung Galaxy A54",
            "description": "128GB, 6GB RAM, Câmera 50MP",
            "price": "450000.00",
            "stock_quantity": 15,
        },
        {
            "name": "Laptop HP Pavilion",
            "description": "Intel i5, 8GB RAM, 256GB SSD",
            "price": "850000.00",
            "stock_quantity": 8,
        },
        {
            "name": "Camisa Polo Masculina",
            "description": "100% Algodão, Várias cores",
            "price": "8500.00",
            "stock_quantity": 50,
        },
        {
            "name": "Livro: Python Para Iniciantes",
            "description": "Guia completo de Python",
            "price": "12000.00",
            "stock_quantity": 25,
        },
        {
            "name": "Mesa de Escritório",
            "description": "1.20m x 0.60m, Madeira MDF",
            "price": "45000.00",
            "stock_quantity": 10,
        },
    ]

    for i, prod_data in enumerate(products_data):
        # Usar categoria correspondente ou primeira se índice maior
        category = created_categories[min(i, len(created_categories) - 1)]

        product, created = Product.objects.get_or_create(
            name=prod_data["name"],
            defaults={
                **prod_data,
                "store": store,
                "category": category,
                "in_stock": True,
                "featured": True,
            },
        )
        status = "✅ Criado" if created else "ℹ️  Já existe"
        print(f"  {status}: {product.name} - {product.price} Kz")

    # 5. Criar comprador
    print("\n👥 Criando comprador...")
    buyer, created = CustomUser.objects.get_or_create(
        username="comprador_teste",
        defaults={
            "email": "comprador@teste.com",
            "first_name": "Comprador",
            "last_name": "Teste",
            "user_type": "buyer",
        },
    )
    if created:
        buyer.set_password("Test@123")
        buyer.save()
        print("  ✅ Comprador criado")
    else:
        print("  ℹ️  Comprador já existe")

    # 6. Criar admin
    print("\n🔑 Criando administrador...")
    admin, created = CustomUser.objects.get_or_create(
        username="admin_teste",
        defaults={
            "email": "admin@teste.com",
            "first_name": "Admin",
            "last_name": "Teste",
            "user_type": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin.set_password("Test@123")
        admin.save()
        print("  ✅ Administrador criado")
    else:
        print("  ℹ️  Administrador já existe")

    # Resumo
    print("\n" + "=" * 60)
    print("✅ DADOS DE TESTE CONFIGURADOS COM SUCESSO!")
    print("=" * 60)
    print("\n📊 Resumo:")
    print(f"  • Categorias: {Category.objects.count()}")
    print(f"  • Produtos: {Product.objects.count()}")
    print(f"  • Usuários: {CustomUser.objects.count()}")
    print(f"  • Lojas: {Store.objects.count()}")

    print("\n🔐 Credenciais de teste:")
    print("  Comprador: comprador_teste / Test@123")
    print("  Vendedor:  vendedor_aprovado / Test@123")
    print("  Admin:     admin_teste / Test@123")

    print("\n🚀 Agora você pode:")
    print("  1. Executar: python test_api_completo.py")
    print("  2. Acessar: http://localhost:8000/api/docs/")
    print("  3. Testar com Postman/Thunder Client")
    print("\n")


if __name__ == "__main__":
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Erro ao criar dados: {str(e)}")
        print("\nSoluções possíveis:")
        print("  1. Execute da raiz do projeto: python setup_test_data.py")
        print("  2. Ou use: python manage.py shell < setup_test_data.py")
        print("  3. Certifique-se de que as migrações foram aplicadas:")
        print("     python manage.py migrate")
        import traceback

        traceback.print_exc()
else:
    # Executado via manage.py shell
    create_test_data()
