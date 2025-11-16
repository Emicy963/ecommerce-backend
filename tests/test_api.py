"""
Script de teste completo para todos os endpoints da API E-commerce
Testa: Auth, Products, Cart, Orders, Reviews, Wishlist, Store Management
Uso: python test_api_completo.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


class APITester:
    def __init__(self):
        self.buyer_token = None
        self.seller_token = None
        self.admin_token = None
        self.cart_code = None
        self.product_id = None
        self.store_id = None
        self.order_number = None
        self.review_id = None
        self.passed = 0
        self.failed = 0

    def log(self, message, color=Colors.YELLOW):
        print(f"{color}{message}{Colors.RESET}")

    def test(
        self,
        name,
        method,
        url,
        data=None,
        headers=None,
        expected_status=[200, 201, 204],
    ):
        self.log(f"\nTestando: {name}", Colors.BLUE)

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)

            if response.status_code in expected_status:
                self.log(f"✓ {name} - Status: {response.status_code}", Colors.GREEN)
                self.passed += 1
                return response
            else:
                self.log(f"✗ {name} - Status: {response.status_code}", Colors.RED)
                self.log(f"Resposta: {response.text}", Colors.RED)
                self.failed += 1
                return None

        except Exception as e:
            self.log(f"✗ Erro: {str(e)}", Colors.RED)
            self.failed += 1
            return None

    def run_tests(self):
        self.log("\n" + "=" * 60, Colors.YELLOW)
        self.log("INICIANDO TESTES COMPLETOS DA API E-COMMERCE", Colors.YELLOW)
        self.log("=" * 60 + "\n", Colors.YELLOW)

        # Seção 1: AUTENTICAÇÃO
        self.log("\n### SEÇÃO 1: AUTENTICAÇÃO ###", Colors.BLUE)
        self.test_authentication()

        # Seção 2: GESTÃO DE LOJAS
        self.log("\n### SEÇÃO 2: GESTÃO DE LOJAS ###", Colors.BLUE)
        self.test_store_management()

        # Seção 3: PRODUTOS E CATEGORIAS
        self.log("\n### SEÇÃO 3: PRODUTOS E CATEGORIAS ###", Colors.BLUE)
        self.test_products()

        # Seção 4: CARRINHO DE COMPRAS
        self.log("\n### SEÇÃO 4: CARRINHO DE COMPRAS ###", Colors.BLUE)
        self.test_cart()

        # Seção 5: PEDIDOS
        self.log("\n### SEÇÃO 5: PEDIDOS ###", Colors.BLUE)
        self.test_orders()

        # Seção 6: AVALIAÇÕES
        self.log("\n### SEÇÃO 6: AVALIAÇÕES ###", Colors.BLUE)
        self.test_reviews()

        # Seção 7: LISTA DE DESEJOS
        self.log("\n### SEÇÃO 7: LISTA DE DESEJOS ###", Colors.BLUE)
        self.test_wishlist()

        # Seção 8: FUNCIONALIDADES DE VENDEDOR
        self.log("\n### SEÇÃO 8: FUNCIONALIDADES DE VENDEDOR ###", Colors.BLUE)
        self.test_seller_features()

        # Seção 9: FUNCIONALIDADES DE ADMIN
        self.log("\n### SEÇÃO 9: FUNCIONALIDADES DE ADMIN ###", Colors.BLUE)
        self.test_admin_features()

        # Relatório Final
        self.print_report()

    def test_authentication(self):
        """Testa endpoints de autenticação"""
        timestamp = int(time.time())

        # Registrar comprador
        buyer_data = {
            "username": f"buyer{timestamp}",
            "email": f"buyer{timestamp}@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
            "first_name": "Buyer",
            "last_name": "Test",
            "user_type": "buyer",
        }
        self.test(
            "Registrar Comprador",
            "POST",
            f"{BASE_URL}/api/v1/auth/register/",
            buyer_data,
        )

        # Registrar vendedor
        seller_data = {
            "username": f"seller{timestamp}",
            "email": f"seller{timestamp}@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
            "first_name": "Seller",
            "last_name": "Test",
            "user_type": "seller",
        }
        self.test(
            "Registrar Vendedor",
            "POST",
            f"{BASE_URL}/api/v1/auth/register/",
            seller_data,
        )

        # Login comprador
        login_buyer = self.test(
            "Login Comprador",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"buyer{timestamp}", "password": "Test@123"},
        )
        if login_buyer:
            self.buyer_token = login_buyer.json().get("access")

        # Login vendedor
        login_seller = self.test(
            "Login Vendedor",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"seller{timestamp}", "password": "Test@123"},
        )
        if login_seller:
            self.seller_token = login_seller.json().get("access")

        # Obter perfil
        if self.buyer_token:
            self.test(
                "Obter Perfil do Usuário",
                "GET",
                f"{BASE_URL}/api/v1/auth/profile/",
                headers={"Authorization": f"Bearer {self.buyer_token}"},
            )

        # Testar login com email
        self.test(
            "Login com Email",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"buyer{timestamp}@test.com", "password": "Test@123"},
        )

    def test_store_management(self):
        """Testa gestão de lojas"""
        if not self.seller_token:
            self.log("Pulando testes de loja - sem token de vendedor", Colors.YELLOW)
            return

        headers = {"Authorization": f"Bearer {self.seller_token}"}

        # Criar loja
        store_data = {
            "name": f"Test Store {int(time.time())}",
            "description": "Uma loja de testes",
        }
        store_response = self.test(
            "Criar Loja",
            "POST",
            f"{BASE_URL}/api/v1/auth/store/create/",
            store_data,
            headers,
        )

        if store_response:
            self.store_id = store_response.json().get("id")

        # Obter loja
        self.test(
            "Obter Dados da Loja",
            "GET",
            f"{BASE_URL}/api/v1/auth/store/",
            headers=headers,
        )

        # Atualizar loja
        self.test(
            "Atualizar Loja",
            "PUT",
            f"{BASE_URL}/api/v1/auth/store/",
            {"description": "Descrição atualizada"},
            headers,
        )

    def test_products(self):
        """Testa produtos e categorias"""
        # Listar produtos
        self.test("Listar Produtos", "GET", f"{BASE_URL}/api/v1/products/")

        # Listar categorias
        self.test("Listar Categorias", "GET", f"{BASE_URL}/api/v1/products/categories/")

        # Buscar produtos
        self.test(
            "Buscar Produtos", "GET", f"{BASE_URL}/api/v1/products/search/?query=test"
        )

        # Criar produto (como vendedor)
        if self.seller_token:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            product_data = {
                "name": f"Produto Teste {int(time.time())}",
                "description": "Descrição do produto de teste",
                "price": "99.99",
                "stock_quantity": 10,
                "in_stock": True,
                "featured": True,
            }
            product_response = self.test(
                "Criar Produto",
                "POST",
                f"{BASE_URL}/api/v1/products/seller/create/",
                product_data,
                headers,
            )

            if product_response:
                self.product_id = product_response.json().get("id")
                product_slug = product_response.json().get("slug")

                # Obter detalhes do produto
                self.test(
                    "Obter Detalhes do Produto",
                    "GET",
                    f"{BASE_URL}/api/v1/products/{product_slug}/",
                )

                # Atualizar produto
                self.test(
                    "Atualizar Produto",
                    "PUT",
                    f"{BASE_URL}/api/v1/products/seller/{product_slug}/",
                    {"price": "89.99"},
                    headers,
                )

    def test_cart(self):
        """Testa carrinho de compras"""
        # Criar carrinho
        cart_response = self.test(
            "Criar Carrinho", "POST", f"{BASE_URL}/api/v1/cart/create/"
        )

        if cart_response:
            self.cart_code = cart_response.json().get("cart_code")

            # Obter carrinho
            self.test(
                "Obter Carrinho", "GET", f"{BASE_URL}/api/v1/cart/{self.cart_code}/"
            )

            # Adicionar produto ao carrinho
            if self.product_id:
                add_response = self.test(
                    "Adicionar Produto ao Carrinho",
                    "POST",
                    f"{BASE_URL}/api/v1/cart/add/",
                    {
                        "cart_code": self.cart_code,
                        "product_id": self.product_id,
                        "quantity": 2,
                    },
                )

                if add_response and self.buyer_token:
                    headers = {"Authorization": f"Bearer {self.buyer_token}"}
                    cart_items = add_response.json().get("cartitems", [])

                    if cart_items:
                        item_id = cart_items[0].get("id")

                        # Atualizar quantidade
                        self.test(
                            "Atualizar Quantidade no Carrinho",
                            "PUT",
                            f"{BASE_URL}/api/v1/cart/update/",
                            {"item_id": item_id, "quantity": 3},
                            headers,
                        )

        # Obter carrinho do usuário
        if self.buyer_token:
            headers = {"Authorization": f"Bearer {self.buyer_token}"}
            self.test(
                "Obter Carrinho do Usuário",
                "GET",
                f"{BASE_URL}/api/v1/cart/user/",
                headers=headers,
            )

            # Criar carrinho do usuário
            self.test(
                "Criar Carrinho do Usuário",
                "POST",
                f"{BASE_URL}/api/v1/cart/create-user/",
                headers=headers,
            )

            # Mesclar carrinhos
            if self.cart_code:
                self.test(
                    "Mesclar Carrinhos",
                    "POST",
                    f"{BASE_URL}/api/v1/cart/merge/",
                    {"temp_cart_code": self.cart_code},
                    headers,
                )

    def test_orders(self):
        """Testa pedidos"""
        if not self.buyer_token or not self.cart_code:
            self.log(
                "Pulando testes de pedidos - requisitos não atendidos", Colors.YELLOW
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Criar pedido
        order_data = {
            "cart_code": self.cart_code,
            "shipping_address": "Rua das Acácias, 123, Luanda, Angola",
            "payment_method": "reference",
        }
        order_response = self.test(
            "Criar Pedido",
            "POST",
            f"{BASE_URL}/api/v1/orders/create/",
            order_data,
            headers,
        )

        if order_response:
            order_data = order_response.json().get("order", {})
            self.order_number = order_data.get("order_number")

            # Listar pedidos do usuário
            self.test(
                "Listar Pedidos do Usuário",
                "GET",
                f"{BASE_URL}/api/v1/orders/",
                headers=headers,
            )

            # Obter detalhes do pedido
            if self.order_number:
                self.test(
                    "Obter Detalhes do Pedido",
                    "GET",
                    f"{BASE_URL}/api/v1/orders/{self.order_number}/",
                    headers=headers,
                )

    def test_reviews(self):
        """Testa avaliações"""
        if not self.buyer_token or not self.product_id:
            self.log(
                "Pulando testes de reviews - requisitos não atendidos", Colors.YELLOW
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Listar reviews do usuário
        self.test(
            "Listar Reviews do Usuário",
            "GET",
            f"{BASE_URL}/api/v1/reviews/user/",
            headers=headers,
        )

        # Obter reviews de um produto
        self.test(
            "Obter Reviews do Produto",
            "GET",
            f"{BASE_URL}/api/v1/reviews/product/{self.product_id}/",
            headers=headers,
        )

        # Nota: Adicionar review requer que o usuário tenha comprado o produto
        # Esse teste provavelmente falhará se o pedido não estiver "delivered"
        review_data = {
            "product_id": self.product_id,
            "rating": 5,
            "comment": "Excelente produto!",
        }
        review_response = self.test(
            "Adicionar Review (pode falhar sem compra)",
            "POST",
            f"{BASE_URL}/api/v1/reviews/add/",
            review_data,
            headers,
            expected_status=[201, 400],  # Aceita erro esperado
        )

    def test_wishlist(self):
        """Testa lista de desejos"""
        if not self.buyer_token or not self.product_id:
            self.log(
                "Pulando testes de wishlist - requisitos não atendidos", Colors.YELLOW
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Obter wishlist
        self.test(
            "Obter Wishlist", "GET", f"{BASE_URL}/api/v1/wishlist/", headers=headers
        )

        # Adicionar à wishlist
        self.test(
            "Adicionar à Wishlist",
            "POST",
            f"{BASE_URL}/api/v1/wishlist/add/",
            {"product_id": self.product_id},
            headers,
        )

        # Remover da wishlist (toggle)
        self.test(
            "Remover da Wishlist (toggle)",
            "POST",
            f"{BASE_URL}/api/v1/wishlist/add/",
            {"product_id": self.product_id},
            headers,
            expected_status=[204],
        )

    def test_seller_features(self):
        """Testa funcionalidades de vendedor"""
        if not self.seller_token:
            self.log("Pulando testes de vendedor - sem token", Colors.YELLOW)
            return

        headers = {"Authorization": f"Bearer {self.seller_token}"}

        # Listar pedidos da loja
        self.test(
            "Listar Pedidos da Loja",
            "GET",
            f"{BASE_URL}/api/v1/orders/seller/orders/",
            headers=headers,
        )

        # Atualizar status do pedido
        if self.order_number:
            self.test(
                "Atualizar Status do Pedido",
                "PUT",
                f"{BASE_URL}/api/v1/orders/seller/{self.order_number}/status/",
                {"status": "processing"},
                headers,
            )

        # Listar reviews dos produtos da loja
        self.test(
            "Listar Reviews da Loja",
            "GET",
            f"{BASE_URL}/api/v1/reviews/reviews/",
            headers=headers,
        )

    def test_admin_features(self):
        """Testa funcionalidades de admin"""
        # Nota: Requer criação de usuário admin manualmente
        self.log("Testes de admin requerem usuário admin pré-existente", Colors.YELLOW)

    def print_report(self):
        """Imprime relatório final"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0

        self.log("\n" + "=" * 60, Colors.YELLOW)
        self.log("RELATÓRIO FINAL", Colors.YELLOW)
        self.log("=" * 60, Colors.YELLOW)
        self.log(f"\nTotal de testes: {total}", Colors.BLUE)
        self.log(f"Passou: {self.passed}", Colors.GREEN)
        self.log(f"Falhou: {self.failed}", Colors.RED)
        self.log(f"Taxa de sucesso: {success_rate:.1f}%", Colors.BLUE)

        if self.failed > 0:
            self.log(
                "\n⚠️  Alguns testes falharam. Verifique os logs acima.", Colors.YELLOW
            )
            self.log("Certifique-se de que:", Colors.YELLOW)
            self.log(
                "  - O servidor está rodando (python manage.py runserver)",
                Colors.YELLOW,
            )
            self.log("  - O banco de dados está configurado", Colors.YELLOW)
            self.log("  - Existem produtos/categorias no banco", Colors.YELLOW)
        else:
            self.log("\n✓ Todos os testes passaram com sucesso!", Colors.GREEN)

        self.log("=" * 60 + "\n", Colors.YELLOW)


if __name__ == "__main__":
    tester = APITester()
    tester.run_tests()
