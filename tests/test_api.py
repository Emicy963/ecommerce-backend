"""
Script de teste completo para todos os endpoints da API E-commerce
Uso: python tests/test_api.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"


class APITester:
    def __init__(self):
        self.buyer_token = None
        self.seller_token = None
        self.admin_token = None
        self.cart_code = None
        self.user_cart_code = None
        self.product_id = None
        self.product_slug = None
        self.store_id = None
        self.order_number = None
        self.review_id = None
        self.wishlist_item_id = None
        self.seller_id = None
        self.passed = 0
        self.failed = 0
        self.timestamp = int(time.time())

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
        self.log(f"\n🧪 Testando: {name}", Colors.BLUE)

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
                self.log(f"✅ {name} - Status: {response.status_code}", Colors.GREEN)
                self.passed += 1
                return response
            else:
                self.log(f"❌ {name} - Status: {response.status_code}", Colors.RED)
                self.log(f"Resposta: {response.text}", Colors.RED)
                self.failed += 1
                return None

        except Exception as e:
            self.log(f"❌ Erro: {str(e)}", Colors.RED)
            self.failed += 1
            return None

    def run_tests(self):
        self.log("\n" + "=" * 70, Colors.MAGENTA)
        self.log("🚀 INICIANDO TESTES COMPLETOS DA API E-COMMERCE v2.0", Colors.MAGENTA)
        self.log("=" * 70 + "\n", Colors.MAGENTA)

        # Seção 1: AUTENTICAÇÃO
        self.log("\n### SEÇÃO 1: AUTENTICAÇÃO ###", Colors.BLUE)
        self.test_authentication()

        # Seção 2: ADMIN - APROVAR VENDEDOR
        self.log("\n### SEÇÃO 2: FUNCIONALIDADES DE ADMIN ###", Colors.BLUE)
        self.test_admin_features()

        # Seção 3: GESTÃO DE LOJAS
        self.log("\n### SEÇÃO 3: GESTÃO DE LOJAS ###", Colors.BLUE)
        self.test_store_management()

        # Seção 4: PRODUTOS E CATEGORIAS
        self.log("\n### SEÇÃO 4: PRODUTOS E CATEGORIAS ###", Colors.BLUE)
        self.test_products()

        # Seção 5: CARRINHO DE COMPRAS
        self.log("\n### SEÇÃO 5: CARRINHO DE COMPRAS ###", Colors.BLUE)
        self.test_cart()

        # Seção 6: PEDIDOS
        self.log("\n### SEÇÃO 6: PEDIDOS ###", Colors.BLUE)
        self.test_orders()

        # Seção 7: AVALIAÇÕES
        self.log("\n### SEÇÃO 7: AVALIAÇÕES ###", Colors.BLUE)
        self.test_reviews()

        # Seção 8: LISTA DE DESEJOS
        self.log("\n### SEÇÃO 8: LISTA DE DESEJOS ###", Colors.BLUE)
        self.test_wishlist()

        # Seção 9: FUNCIONALIDADES DE VENDEDOR
        self.log("\n### SEÇÃO 9: FUNCIONALIDADES DE VENDEDOR ###", Colors.BLUE)
        self.test_seller_features()

        # Relatório Final
        self.print_report()

    def test_authentication(self):
        """Testa endpoints de autenticação"""

        # Registrar comprador
        buyer_data = {
            "username": f"buyer{self.timestamp}",
            "email": f"buyer{self.timestamp}@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
            "first_name": "Comprador",
            "last_name": "Teste",
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
            "username": f"seller{self.timestamp}",
            "email": f"seller{self.timestamp}@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
            "first_name": "Vendedor",
            "last_name": "Teste",
            "user_type": "seller",
        }
        self.test(
            "Registrar Vendedor",
            "POST",
            f"{BASE_URL}/api/v1/auth/register/",
            seller_data,
        )

        # Registrar admin
        admin_data = {
            "username": f"admin{self.timestamp}",
            "email": f"admin{self.timestamp}@test.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
            "first_name": "Admin",
            "last_name": "Teste",
            "user_type": "admin",
        }
        self.test(
            "Registrar Administrador",
            "POST",
            f"{BASE_URL}/api/v1/auth/register/",
            admin_data,
        )

        # Login comprador
        login_buyer = self.test(
            "Login Comprador",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"buyer{self.timestamp}", "password": "Test@123"},
        )
        if login_buyer:
            self.buyer_token = login_buyer.json().get("access")

        # Login vendedor
        login_seller = self.test(
            "Login Vendedor",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"seller{self.timestamp}", "password": "Test@123"},
        )
        if login_seller:
            self.seller_token = login_seller.json().get("access")
            user_data = login_seller.json().get("user", {})
            self.seller_id = user_data.get("id")

        # Login admin
        login_admin = self.test(
            "Login Administrador",
            "POST",
            f"{BASE_URL}/api/v1/auth/token/",
            {"username": f"admin{self.timestamp}", "password": "Test@123"},
        )
        if login_admin:
            self.admin_token = login_admin.json().get("access")

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
            {"username": f"buyer{self.timestamp}@test.com", "password": "Test@123"},
        )

    def test_admin_features(self):
        """Testa funcionalidades de admin - APROVAR VENDEDOR"""
        if not self.admin_token or not self.seller_id:
            self.log(
                "⚠️  Pulando aprovação de vendedor - sem admin ou seller_id",
                Colors.YELLOW,
            )
            return

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Listar vendedores pendentes
        self.test(
            "Listar Vendedores Pendentes",
            "GET",
            f"{BASE_URL}/api/v1/auth/admin/pending-sellers/",
            headers=headers,
        )

        # Aprovar vendedor
        self.test(
            "Aprovar Vendedor",
            "POST",
            f"{BASE_URL}/api/v1/auth/admin/approve-seller/{self.seller_id}/",
            headers=headers,
        )

        self.log("✨ Vendedor aprovado! Agora pode criar produtos.", Colors.GREEN)

    def test_store_management(self):
        """Testa gestão de lojas"""
        if not self.seller_token:
            self.log("⚠️  Pulando testes de loja - sem token de vendedor", Colors.YELLOW)
            return

        headers = {"Authorization": f"Bearer {self.seller_token}"}

        # Criar loja
        store_data = {
            "name": f"Loja Teste {self.timestamp}",
            "description": "Uma loja de testes automática",
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
            {"description": "Descrição atualizada automaticamente"},
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

        # Criar produto (como vendedor APROVADO)
        if self.seller_token:
            headers = {"Authorization": f"Bearer {self.seller_token}"}
            product_data = {
                "name": f"Produto Teste {self.timestamp}",
                "description": "Descrição do produto de teste automático",
                "price": "99999.99",
                "stock_quantity": 100,
                "in_stock": True,
                "featured": True,
            }
            product_response = self.test(
                "Criar Produto (Vendedor Aprovado)",
                "POST",
                f"{BASE_URL}/api/v1/products/seller/create/",
                product_data,
                headers,
            )

            if product_response:
                product_json = product_response.json()
                self.product_id = product_json.get("id")
                self.product_slug = product_json.get("slug")

                self.log(
                    f"📦 Produto criado: ID={self.product_id}, Slug={self.product_slug}",
                    Colors.GREEN,
                )

                # Obter detalhes do produto
                if self.product_slug:
                    self.test(
                        "Obter Detalhes do Produto",
                        "GET",
                        f"{BASE_URL}/api/v1/products/{self.product_slug}/",
                    )

                    # Atualizar produto
                    self.test(
                        "Atualizar Produto",
                        "PUT",
                        f"{BASE_URL}/api/v1/products/seller/{self.product_slug}/",
                        {"price": "89999.99"},
                        headers,
                    )

    def test_cart(self):
        """Testa carrinho de compras"""
        # Criar carrinho anônimo
        cart_response = self.test(
            "Criar Carrinho Anônimo", "POST", f"{BASE_URL}/api/v1/cart/create/"
        )

        if cart_response:
            self.cart_code = cart_response.json().get("cart_code")
            self.log(f"🛒 Carrinho criado: {self.cart_code}", Colors.GREEN)

            # Obter carrinho
            self.test(
                "Obter Carrinho Anônimo",
                "GET",
                f"{BASE_URL}/api/v1/cart/{self.cart_code}/",
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

                # Testes autenticados
                if self.buyer_token:
                    headers = {"Authorization": f"Bearer {self.buyer_token}"}

                    # Criar carrinho do usuário
                    user_cart_response = self.test(
                        "Criar Carrinho do Usuário",
                        "POST",
                        f"{BASE_URL}/api/v1/cart/create-user/",
                        headers=headers,
                    )

                    if user_cart_response:
                        self.user_cart_code = user_cart_response.json().get("cart_code")

                    # Obter carrinho do usuário
                    self.test(
                        "Obter Carrinho do Usuário",
                        "GET",
                        f"{BASE_URL}/api/v1/cart/user/",
                        headers=headers,
                    )

                    # Mesclar carrinhos
                    self.test(
                        "Mesclar Carrinhos",
                        "POST",
                        f"{BASE_URL}/api/v1/cart/merge/",
                        {"temp_cart_code": self.cart_code},
                        headers,
                    )

                    # Atualizar carrinho do usuário para usar nos pedidos
                    final_cart = self.test(
                        "Obter Carrinho Final do Usuário",
                        "GET",
                        f"{BASE_URL}/api/v1/cart/user/",
                        headers=headers,
                    )

                    if final_cart:
                        self.user_cart_code = final_cart.json().get("cart_code")
                        self.log(
                            f"🛒 Carrinho do usuário: {self.user_cart_code}",
                            Colors.GREEN,
                        )

                        # Atualizar quantidade de item
                        cart_items = final_cart.json().get("cartitems", [])
                        if cart_items:
                            item_id = cart_items[0].get("id")
                            self.test(
                                "Atualizar Quantidade no Carrinho",
                                "PUT",
                                f"{BASE_URL}/api/v1/cart/update/",
                                {"item_id": item_id, "quantity": 3},
                                headers,
                            )

    def test_orders(self):
        """Testa pedidos"""
        if not self.buyer_token or not self.user_cart_code:
            self.log(
                "⚠️  Pulando testes de pedidos - sem token ou carrinho do usuário",
                Colors.YELLOW,
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Criar pedido
        order_data = {
            "cart_code": self.user_cart_code,
            "shipping_address": "Rua das Acácias, 123, Luanda, Talatona, Angola",
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
            order_json = order_response.json()
            order_data = order_json.get("order", {})
            self.order_number = order_data.get("order_number")

            self.log(f"📦 Pedido criado: {self.order_number}", Colors.GREEN)

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
                "⚠️  Pulando testes de reviews - sem token ou produto", Colors.YELLOW
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Obter reviews de um produto
        self.test(
            "Obter Reviews do Produto",
            "GET",
            f"{BASE_URL}/api/v1/reviews/product/{self.product_id}/",
            headers=headers,
        )

        # Listar reviews do usuário
        self.test(
            "Listar Reviews do Usuário",
            "GET",
            f"{BASE_URL}/api/v1/reviews/user/",
            headers=headers,
        )

        # Tentar adicionar review (pode falhar se pedido não foi entregue)
        review_data = {
            "product_id": self.product_id,
            "rating": 5,
            "comment": "Excelente produto! Teste automático.",
        }
        review_response = self.test(
            "Adicionar Review (pode falhar sem compra entregue)",
            "POST",
            f"{BASE_URL}/api/v1/reviews/add/",
            review_data,
            headers,
            expected_status=[201, 400],  # Aceita erro esperado
        )

        if review_response and review_response.status_code == 201:
            self.review_id = review_response.json().get("id")
            self.log(f"⭐ Review criado: ID={self.review_id}", Colors.GREEN)

            # Atualizar review
            self.test(
                "Atualizar Review",
                "PUT",
                f"{BASE_URL}/api/v1/reviews/{self.review_id}/",
                {"rating": 4, "comment": "Atualizado para 4 estrelas"},
                headers,
            )
        else:
            self.log(
                "ℹ️  Review não criado (esperado - requer pedido entregue)",
                Colors.YELLOW,
            )

    def test_wishlist(self):
        """Testa lista de desejos"""
        if not self.buyer_token or not self.product_id:
            self.log(
                "⚠️  Pulando testes de wishlist - sem token ou produto", Colors.YELLOW
            )
            return

        headers = {"Authorization": f"Bearer {self.buyer_token}"}

        # Obter wishlist vazia
        self.test(
            "Obter Wishlist (vazia)",
            "GET",
            f"{BASE_URL}/api/v1/wishlist/",
            headers=headers,
        )

        # Adicionar à wishlist
        wishlist_response = self.test(
            "Adicionar à Wishlist",
            "POST",
            f"{BASE_URL}/api/v1/wishlist/add/",
            {"product_id": self.product_id},
            headers,
        )

        if wishlist_response:
            self.wishlist_item_id = wishlist_response.json().get("id")
            self.log(
                f"❤️  Produto adicionado à wishlist: ID={self.wishlist_item_id}",
                Colors.GREEN,
            )

        # Obter wishlist com item
        self.test(
            "Obter Wishlist (com item)",
            "GET",
            f"{BASE_URL}/api/v1/wishlist/",
            headers=headers,
        )

        # Remover da wishlist (usando o mesmo endpoint - toggle)
        self.test(
            "Remover da Wishlist (toggle)",
            "POST",
            f"{BASE_URL}/api/v1/wishlist/add/",
            {"product_id": self.product_id},
            headers,
            expected_status=[204],
        )

        # Verificar wishlist vazia novamente
        self.test(
            "Verificar Wishlist Vazia",
            "GET",
            f"{BASE_URL}/api/v1/wishlist/",
            headers=headers,
        )

    def test_seller_features(self):
        """Testa funcionalidades de vendedor"""
        if not self.seller_token:
            self.log("⚠️  Pulando testes de vendedor - sem token", Colors.YELLOW)
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

            # Atualizar para shipped
            self.test(
                "Atualizar Status para Enviado",
                "PUT",
                f"{BASE_URL}/api/v1/orders/seller/{self.order_number}/status/",
                {"status": "shipped"},
                headers,
            )

        # Listar reviews dos produtos da loja
        self.test(
            "Listar Reviews da Loja",
            "GET",
            f"{BASE_URL}/api/v1/reviews/reviews/",
            headers=headers,
        )

    def print_report(self):
        """Imprime relatório final"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0

        self.log("\n" + "=" * 70, Colors.MAGENTA)
        self.log("📊 RELATÓRIO FINAL DE TESTES", Colors.MAGENTA)
        self.log("=" * 70, Colors.MAGENTA)
        self.log(f"\n📈 Total de testes: {total}", Colors.BLUE)
        self.log(f"✅ Passou: {self.passed}", Colors.GREEN)
        self.log(f"❌ Falhou: {self.failed}", Colors.RED)
        self.log(f"📊 Taxa de sucesso: {success_rate:.1f}%", Colors.BLUE)

        # Resumo dos IDs criados
        self.log("\n" + "-" * 70, Colors.YELLOW)
        self.log("🔑 IDs e Códigos Gerados:", Colors.YELLOW)
        self.log("-" * 70, Colors.YELLOW)
        if self.seller_id:
            self.log(f"👤 Seller ID: {self.seller_id}", Colors.YELLOW)
        if self.store_id:
            self.log(f"🏪 Store ID: {self.store_id}", Colors.YELLOW)
        if self.product_id:
            self.log(f"📦 Product ID: {self.product_id}", Colors.YELLOW)
        if self.product_slug:
            self.log(f"🔗 Product Slug: {self.product_slug}", Colors.YELLOW)
        if self.cart_code:
            self.log(f"🛒 Cart Code (anônimo): {self.cart_code}", Colors.YELLOW)
        if self.user_cart_code:
            self.log(f"🛒 User Cart Code: {self.user_cart_code}", Colors.YELLOW)
        if self.order_number:
            self.log(f"📋 Order Number: {self.order_number}", Colors.YELLOW)
        if self.review_id:
            self.log(f"⭐ Review ID: {self.review_id}", Colors.YELLOW)
        if self.wishlist_item_id:
            self.log(f"❤️  Wishlist Item ID: {self.wishlist_item_id}", Colors.YELLOW)

        self.log("\n" + "-" * 70, Colors.YELLOW)

        if self.failed > 0:
            self.log(
                "\n⚠️  Alguns testes falharam. Verifique os logs acima.", Colors.YELLOW
            )
            self.log("Certifique-se de que:", Colors.YELLOW)
            self.log(
                "  ✓ O servidor está rodando (python manage.py runserver)",
                Colors.YELLOW,
            )
            self.log("  ✓ O banco de dados está configurado", Colors.YELLOW)
            self.log("  ✓ As migrações foram aplicadas", Colors.YELLOW)
        else:
            self.log("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!", Colors.GREEN)
            self.log("✨ Sistema funcionando perfeitamente!", Colors.GREEN)

        self.log("\n" + "=" * 70 + "\n", Colors.MAGENTA)


if __name__ == "__main__":
    print("\n🚀 Iniciando testes da API E-commerce...")
    print("⏱️  Isso pode levar alguns minutos...\n")

    tester = APITester()
    tester.run_tests()
