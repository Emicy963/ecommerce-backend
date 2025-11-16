# 📘 Manual Técnico - Sistema E-commerce

> Documentação técnica completa da arquitetura, funcionamento e implementação do sistema de e-commerce.

---

## 📑 Índice

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Modelos de Dados](#2-modelos-de-dados)
3. [Sistema de Autenticação](#3-sistema-de-autenticação)
4. [Fluxos de Negócio](#4-fluxos-de-negócio)
5. [API Endpoints](#5-api-endpoints)
6. [Sistema de Pagamento](#6-sistema-de-pagamento)
7. [Segurança](#7-segurança)
8. [Performance e Otimizações](#8-performance-e-otimizações)
9. [Tratamento de Erros](#9-tratamento-de-erros)
10. [Deploy e Escalabilidade](#10-deploy-e-escalabilidade)

---

## 1. Visão Geral da Arquitetura

### 1.1 Stack Tecnológico

```md
┌─────────────────────────────────────────────┐
│           FRONTEND (React/Vue/Angular)      │
│              HTTP/HTTPS Requests            │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Django REST Framework (DRF)         │
│   ┌─────────────────────────────────────┐   │
│   │  Authentication (SimpleJWT)         │   │
│   │  Permissions & Authorization        │   │
│   │  Serialization & Validation         │   │
│   └─────────────────────────────────────┘   │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│            Django ORM (Models)              │
│   ┌─────────────────────────────────────┐   │
│   │  Business Logic                     │   │
│   │  Data Validation                    │   │
│   │  Relationships                      │   │
│   └─────────────────────────────────────┘   │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│        Database (SQLite/PostgreSQL)         │
│   ┌─────────────────────────────────────┐   │
│   │  Users, Products, Orders, etc.      │   │
│   └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 1.2 Estrutura de Apps Django

O projeto segue o padrão de **apps modulares** do Django:

```md
apps/
├── accounts/     → Usuários, lojas, autenticação
├── products/     → Produtos, categorias, busca
├── cart/         → Carrinho de compras
├── orders/       → Pedidos, pagamentos
├── reviews/      → Avaliações e ratings
└── wishlist/     → Lista de desejos
```

**Vantagens:**

- ✅ Separação de responsabilidades
- ✅ Fácil manutenção
- ✅ Testável individualmente
- ✅ Reutilizável em outros projetos

---

## 2. Modelos de Dados

### 2.1 Diagrama ER (Entidade-Relacionamento)

```md
┌──────────────┐
│ CustomUser   │
│──────────────│
│ id           │◄────┐
│ username     │     │
│ email        │     │ 1:1
│ user_type    │     │
│ is_approved  │     │
└──────────────┘     │
       │             │
       │ 1:1         │
       ▼             │
┌──────────────┐     │
│    Store     │     │
│──────────────│     │
│ id           │     │
│ name         │─────┘
│ slug         │
│ owner_id     │
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│   Product    │
│──────────────│
│ id           │◄────────┐
│ name         │         │
│ price        │         │
│ stock        │         │
│ store_id     │         │
│ category_id  │         │
└──────────────┘         │
       │                 │
       │ 1:N             │ N:1
       ▼                 │
┌──────────────┐         │
│   Review     │         │
│──────────────│         │
│ product_id   │─────────┤
│ user_id      │         │
│ rating       │         │
└──────────────┘         │
                         │
┌──────────────┐         │
│   CartItem   │         │
│──────────────│         │
│ cart_id      │         │
│ product_id   │─────────┤
│ quantity     │         │
└──────────────┘         │
       ▲                 │
       │ N:1             │
       │                 │
┌──────────────┐         │
│     Cart     │         │
│──────────────│         │
│ cart_code    │         │
│ user_id      │         │
└──────────────┘         │
                         │
┌──────────────┐         │
│  OrderItem   │         │
│──────────────│         │
│ order_id     │         │
│ product_id   │─────────┘
│ quantity     │
│ price        │
└──────────────┘
       ▲
       │ N:1
       │
┌──────────────┐
│    Order     │
│──────────────│
│ order_number │
│ user_id      │
│ status       │
│ total_amount │
└──────────────┘
       │
       │ 1:1
       ▼
┌──────────────┐
│   Payment    │
│──────────────│
│ order_id     │
│ method       │
│ status       │
│ transaction  │
└──────────────┘
```

### 2.2 Modelos Detalhados

#### **CustomUser** (apps/accounts/models.py)

```python
class CustomUser(AbstractUser):
    TYPE_USER = [
        ("buyer", "Comprador"),
        ("seller", "Vendedor"),
        ("admin", "Administrador"),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=TYPE_USER)
    is_approved_seller = models.BooleanField(default=False)
    # ... outros campos
```

**Características:**

- Herda de `AbstractUser` (Django)
- Suporta 3 tipos de usuário
- Email único para login
- Vendedores requerem aprovação

#### **Store** (apps/accounts/models.py)

```python
class Store(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    # ... outros campos
```

**Características:**

- Relação 1:1 com vendedor
- Slug gerado automaticamente
- Pode ser desativada (soft delete)

#### **Product** (apps/products/models.py)

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ... outros campos
```

**Características:**

- Relação N:1 com Store e Category
- Controle automático de estoque
- Slug único gerado do nome

#### **Cart & CartItem** (apps/cart/models.py)

```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    cart_code = models.CharField(max_length=11, unique=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = [["cart", "product"]]
```

**Características:**

- Carrinho pode ser anônimo (sem user) ou autenticado
- `cart_code` permite carrinho sem login
- `unique_together` impede duplicatas
- Mesclagem automática ao fazer login

#### **Order, OrderItem & Payment** (apps/orders/models.py)

```python
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("confirmed", "Confirmado"),
        ("processing", "Em Processamento"),
        ("shipped", "Enviado"),
        ("delivered", "Entregue"),
        ("cancelled", "Cancelado"),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # ... outros campos
```

**Características:**

- `order_number` gerado automaticamente (UUID)
- Múltiplos status para rastreamento
- Snapshot do preço no `OrderItem` (não referencia preço atual)

#### **Review & ProductRating** (apps/reviews/models.py)

```python
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, "Ruim"), ...])
    comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ["product", "user"]

class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
```

**Características:**

- Um usuário só pode avaliar cada produto uma vez
- `ProductRating` atualizado automaticamente via signals
- Reviews só permitidos após compra

---

## 3. Sistema de Autenticação

### 3.1 Fluxo de Autenticação JWT

```md
┌─────────┐                                    ┌─────────┐
│ Cliente │                                    │  API    │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  POST /auth/token/                           │
     │  {username, password}                        │
     ├─────────────────────────────────────────────►│
     │                                              │
     │                     Valida credenciais       │
     │                     Gera Access Token        │
     │                     Gera Refresh Token       │
     │                                              │
     │  200 OK                                      │
     │  {access, refresh, user}                     │
     │◄─────────────────────────────────────────────┤
     │                                              │
     │  GET /products/ (com token)                  │
     │  Authorization: Bearer <access_token>        │
     ├─────────────────────────────────────────────►│
     │                                              │
     │                     Valida token             │
     │                     Verifica expiração       │
     │                     Extrai user_id           │
     │                                              │
     │  200 OK                                      │
     │  {produtos}                                  │
     │◄─────────────────────────────────────────────┤
     │                                              │
     │  (Token expira após 1h)                      │
     │                                              │
     │  POST /auth/token/refresh/                   │
     │  {refresh}                                   │
     ├─────────────────────────────────────────────►│
     │                                              │
     │                     Valida refresh token     │
     │                     Gera novo access token   │
     │                                              │
     │  200 OK                                      │
     │  {access}                                    │
     │◄─────────────────────────────────────────────┤
```

### 3.2 Configuração JWT

```python
# settings.py
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

**Funcionamento:**

1. **Access Token**: Válido por 1 hora, usado em todas as requisições
2. **Refresh Token**: Válido por 7 dias, usado para renovar access token
3. **Blacklist**: Tokens invalidados após logout
4. **Rotation**: Novo refresh token a cada renovação

### 3.3 Permissões Customizadas

```python
# Exemplo de permissão
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

**Níveis de Permissão:**

- `AllowAny`: Acesso público
- `IsAuthenticated`: Requer login
- `IsAdminUser`: Apenas admin
- Customizadas: `IsOwner`, `IsSeller`, etc.

---

## 4. Fluxos de Negócio

### 4.1 Fluxo de Compra Completo

```md
[1] Cliente navega produtos
        │
        ▼
[2] Adiciona ao carrinho (anônimo ou autenticado)
        │
        ▼
[3] Cliente faz login/registro
        │
        ▼
[4] Carrinhos são mesclados (se aplicável)
        │
        ▼
[5] Cliente finaliza pedido
        │
        ├─ Valida estoque
        ├─ Calcula total
        └─ Cria Order
        │
        ▼
[6] Processamento de pagamento
        │
        ├─ Sucesso: Order status = "confirmed"
        │           Estoque decrementado
        │           Carrinho limpo
        │
        └─ Falha: Order status = "cancelled"
                  Estoque devolvido
                  Carrinho mantido
        │
        ▼
[7] Cliente pode acompanhar pedido
        │
        ▼
[8] Vendedor atualiza status (processing → shipped → delivered)
        │
        ▼
[9] Cliente pode avaliar produto (após delivered)
```

### 4.2 Fluxo de Gestão de Estoque

```python
# apps/orders/views.py (create_order)
with transaction.atomic():
    # 1. Criar pedido
    order = Order.objects.create(...)
    
    # 2. Para cada item do carrinho
    for cart_item in cart.cartitems.all():
        # 2.1 Verificar estoque
        if product.stock_quantity < cart_item.quantity:
            raise Exception("Estoque insuficiente")
        
        # 2.2 Criar OrderItem
        OrderItem.objects.create(...)
        
        # 2.3 Decrementar estoque
        product.stock_quantity -= cart_item.quantity
        if product.stock_quantity == 0:
            product.in_stock = False
        product.save()
    
    # 3. Processar pagamento
    success, transaction_id, message = process_payment(...)
    
    if success:
        # Commit automático
        return success_response
    else:
        # Rollback automático (transaction.atomic())
        raise Exception("Pagamento falhou")
```

**Proteções:**

- ✅ `transaction.atomic()`: Garante atomicidade
- ✅ `select_for_update()`: Evita race conditions
- ✅ Validação de estoque antes de decrementar
- ✅ Rollback automático em caso de erro

### 4.3 Fluxo de Avaliações com Signals

```python
# apps/reviews/signals.py
@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    product = instance.product
    
    # Calcular nova média
    stats = product.reviews.aggregate(
        avg_rating=Avg("rating"),
        total=Count("id")
    )
    
    # Atualizar ProductRating
    ProductRating.objects.update_or_create(
        product=product,
        defaults={
            "average_rating": stats["avg_rating"] or 0.0,
            "total_reviews": stats["total"]
        }
    )
```

**Vantagens:**

- ✅ Atualização automática
- ✅ Código desacoplado
- ✅ Funciona para save() e delete()

---

## 5. API Endpoints

### 5.1 Padrão de Resposta

**Sucesso (200/201):**

```json
{
  "id": 1,
  "name": "Produto X",
  "price": "99.99",
  "in_stock": true
}
```

**Erro (400/404/500):**

```json
{
  "error": "Mensagem descritiva do erro"
}
```

**Lista (200):**

```json
[
  {
    "id": 1,
    "name": "Produto 1"
  },
  {
    "id": 2,
    "name": "Produto 2"
  }
]
```

### 5.2 Paginação

DRF usa paginação automática (configurado em settings.py):

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

**Resposta paginada:**

```json
{
  "count": 100,
  "next": "http://api.example.org/products/?page=2",
  "previous": null,
  "results": [...]
}
```

### 5.3 Filtros e Busca

```python
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

**Exemplos:**

```md
GET /products/?search=laptop
GET /products/?category=eletronicos
GET /products/?ordering=-created_at
GET /products/?min_price=100&max_price=500
```

---

## 6. Sistema de Pagamento

### 6.1 Arquitetura do Processador

```python
# apps/orders/payments.py
class AOAPaymentProcessor:
    @staticmethod
    def process_payment(order, payment_method, reference_number=None):
        # 1. Criar registro de pagamento
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount
        )
        
        # 2. Simular processamento
        if settings.TESTING:
            success = True
        else:
            success = random.choice([True, True, True, False])
        
        # 3. Atualizar status
        if success:
            payment.transaction_id = generate_transaction_id()
            payment.payment_status = "completed"
            order.payment_status = "paid"
            order.status = "confirmed"
        else:
            payment.payment_status = "failed"
            order.payment_status = "failed"
        
        payment.save()
        order.save()
        
        return success, payment.transaction_id, message
```

### 6.2 Métodos de Pagamento

1. **Pagamento por Referência** (`reference`)
   - Gera número de referência
   - Cliente paga em banco/ATM
   - Confirmação manual ou webhook

2. **Pagamento Móvel** (`mobile`)
   - Integração com Express Payment, Multicaixa, etc.
   - Confirmação via API do gateway

3. **Cartão de Crédito** (`card`)
   - Tokenização do cartão
   - Processamento via gateway

### 6.3 Integração Real (Produção)

Para produção, substitua a simulação por integração real:

```python
# Exemplo com gateway fictício
import requests

def process_payment_real(order, payment_method):
    gateway_url = "https://gateway.ao/api/payments"
    
    payload = {
        "amount": float(order.total_amount),
        "currency": "AOA",
        "reference": order.order_number,
        "method": payment_method,
        "callback_url": f"{settings.SITE_URL}/api/v1/orders/callback/"
    }
    
    headers = {
        "Authorization": f"Bearer {settings.PAYMENT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(gateway_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return True, data["transaction_id"], "Sucesso"
    else:
        return False, None, "Falha no pagamento"
```

---

## 7. Segurança

### 7.1 Validações Implementadas

```python
# 1. Validação de entrada (Serializers)
class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )
    stock_quantity = serializers.IntegerField(min_value=0)

# 2. Validação de permissão (Views)
@permission_classes([IsAuthenticated])
def create_order(request):
    if request.user.user_type != "buyer":
        return Response({"error": "Forbidden"}, status=403)

# 3. Validação de negócio (Models/Views)
if product.stock_quantity < quantity:
    raise ValidationError("Estoque insuficiente")
```

### 7.2 Proteções contra Ataques

**SQL Injection:**

```python
# ❌ NUNCA faça isso
Product.objects.raw(f"SELECT * FROM products WHERE name = '{user_input}'")

# ✅ Use ORM do Django
Product.objects.filter(name=user_input)
```

**XSS (Cross-Site Scripting):**

```python
# Django escapa automaticamente HTML nos templates
# Serializers do DRF sanitizam dados

# Para HTML deliberado, use:
from django.utils.html import escape
safe_html = escape(user_input)
```

**CSRF (Cross-Site Request Forgery):**

```python
# Django CSRF protection ativado por padrão
# Para APIs REST, JWT substitui CSRF

# Se usar sessões:
from django.views.decorators.csrf import csrf_protect
@csrf_protect
def my_view(request):
    ...
```

**Rate Limiting:**

```python
# Instalar: pip install django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def create_order(request):
    ...
```

### 7.3 Checklist de Segurança

- [x] Senhas hasheadas (Django padrão)
- [x] JWT com expiração
- [x] HTTPS obrigatório em produção
- [x] CORS configurado corretamente
- [x] SQL Injection prevenido (ORM)
- [x] XSS prevenido (sanitização)
- [x] Validação de entrada em todos os endpoints
- [x] Permissões por tipo de usuário
- [ ] Rate limiting (implementar em produção)
- [ ] Logs de segurança
- [ ] Backup automático

---

## 8. Performance e Otimizações

### 8.1 Otimizações de Query

```python
# ❌ N+1 Problem
products = Product.objects.all()
for product in products:
    print(product.store.name)  # Query para cada produto

# ✅ Select Related (1:1 e N:1)
products = Product.objects.select_related('store', 'category')
for product in products:
    print(product.store.name)  # Sem queries extras

# ✅ Prefetch Related (M:N e 1:N reverse)
orders = Order.objects.prefetch_related('items__product')
for order in orders:
    for item in order.items.all():
        print(item.product.name)  # Sem queries extras
```

### 8.2 Índices de Banco de Dados

```python
class Product(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'in_stock']),
            models.Index(fields=['-created_at']),
        ]
```

### 8.3 Cache

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# views.py
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache por 15 minutos
def product_list(request):
    ...
```

### 8.4 Compressão de Resposta

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # Adicionar
    # ... outros middlewares
]
```

---

## 9. Tratamento de Erros

### 9.1 Hierarquia de Erros

```md
Exception
│
├─ ValidationError (400)
│
├─ PermissionDenied (403)
│
├─ NotFound (404)
│
└─ APIException (DRF)
   │
   ├─ AuthenticationFailed (401)
   ├─ NotAuthenticated (401)
   ├─ Throttled (429)
   └─ ... outros
```

### 9.2 Handler Global

```python
# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'ecommerce.exceptions.custom_exception_handler'
}

# ecommerce/exceptions.py
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'error': response.data.get('detail', str(exc)),
            'status_code': response.status_code
        }
    
    return response
```

### 9.3 Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# views.py
import logging
logger = logging.getLogger(__name__)

try:
    process_order()
except Exception as e:
    logger.error(f"Erro ao processar pedido: {str(e)}")
    raise
```

---

## 10. Deploy e Escalabilidade

### 10.1 Checklist de Deploy

```bash
# 1. Variáveis de ambiente
DEBUG=False
ALLOWED_HOSTS=seudominio.ao,www.seudominio.ao
SECRET_KEY=chave-forte-aqui

# 2. Banco de dados
python manage.py migrate

# 3. Arquivos estáticos
python manage.py collectstatic --noinput

# 4. Criar superusuário
python manage.py createsuperuser

# 5. Verificar configuração
python manage.py check --deploy

# 6. Iniciar com gunicorn
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000
```

### 10.2 Arquitetura de Produção

```md
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │   CloudFlare   │ (CDN, DDoS protection)
              └────────┬───────┘
                       │
                       ▼
              ┌────────────────┐
              │     Nginx      │ (Reverse Proxy, SSL)
              └────────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌──────────┐    ┌─────────┐    ┌─────────┐
   │PostgreSQL│    │  Redis  │    │   S3    │
   │(Database)│    │ (Cache) │    │ (Media) │
   └──────────┘    └─────────┘    └─────────┘
```

### 10.3 Configuração Nginx

```nginx
# /etc/nginx/sites-available/ecommerce
server {
    listen 80;
    server_name seudominio.ao www.seudominio.ao;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.ao www.seudominio.ao;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/seudominio.ao/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.ao/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Client Max Body Size (para uploads)
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /var/www/ecommerce/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/ecommerce/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API rate limiting
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        # ... outros headers
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 10.4 Gunicorn Configuration

```python
# gunicorn_config.py
import multiprocessing

# Server Socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "ecommerce_api"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
user = "www-data"
group = "www-data"
umask = 0o007

# SSL (se terminar SSL no Gunicorn)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

**Comando para iniciar:**

```bash
gunicorn -c gunicorn_config.py ecommerce.wsgi:application
```

### 10.5 Systemd Service

```ini
# /etc/systemd/system/ecommerce.service
[Unit]
Description=E-commerce Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce
Environment="PATH=/var/www/ecommerce/venv/bin"
ExecStart=/var/www/ecommerce/venv/bin/gunicorn \
          -c gunicorn_config.py \
          ecommerce.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

**Comandos:**

```bash
# Ativar serviço
sudo systemctl enable ecommerce
sudo systemctl start ecommerce

# Verificar status
sudo systemctl status ecommerce

# Reiniciar
sudo systemctl restart ecommerce

# Ver logs
sudo journalctl -u ecommerce -f
```

### 10.6 PostgreSQL para Produção

```python
# settings.py (produção)
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Ou manualmente:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 10.7 Redis para Cache e Sessões

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv("REDIS_PASSWORD"),
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "RETRY_ON_TIMEOUT": True,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True
            }
        }
    }
}

# Usar Redis para sessões
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### 10.8 Arquivos de Media em S3 (AWS)

```python
# settings.py
# pip install django-storages boto3

if not DEBUG:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    
    # Cache control
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
```

### 10.9 Monitoramento

#### **Sentry (Error Tracking)**

```python
# pip install sentry-sdk

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment="production",
    )
```

#### **New Relic (APM)**

```python
# pip install newrelic

# newrelic.ini
[newrelic]
license_key = YOUR_LICENSE_KEY
app_name = E-commerce API
monitor_mode = true
log_level = info

# Iniciar com:
# NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn ...
```

### 10.10 Backup Automático

```bash
#!/bin/bash
# /usr/local/bin/backup_ecommerce.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ecommerce"
DB_NAME="ecommerce_db"
DB_USER="postgres"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/ecommerce/media/

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://ecommerce-backups/db/
aws s3 cp $BACKUP_DIR/media_$DATE.tar.gz s3://ecommerce-backups/media/

# Limpar backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup concluído: $DATE"
```

**Cron job:**

```bash
# crontab -e
0 2 * * * /usr/local/bin/backup_ecommerce.sh
```

### 10.11 Health Check Endpoint

```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Endpoint para monitoramento de saúde do sistema"""
    try:
        # Testar conexão com banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "timestamp": timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": timezone.now().isoformat()
        }, status=500)

# urls.py
urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... outras rotas
]
```

### 10.12 Escalabilidade Horizontal

```md
                Load Balancer (HAProxy/AWS ELB)
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
    Server 1            Server 2            Server 3
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Nginx   │        │ Nginx   │        │ Nginx   │
   │ Django  │        │ Django  │        │ Django  │
   └─────────┘        └─────────┘        └─────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        PostgreSQL (Master)      Redis Cluster
                │
                ▼
        PostgreSQL (Replica)
```

**Considerações:**

- **Sessões**: Usar Redis ou banco de dados (não arquivos)
- **Media**: Usar S3 ou CDN compartilhado
- **Cache**: Redis Cluster para alta disponibilidade
- **Database**: Master-Replica para leitura/escrita

---

## 11. Manutenção e Troubleshooting

### 11.1 Comandos Úteis

```bash
# Verificar erros de configuração
python manage.py check

# Verificar configuração para produção
python manage.py check --deploy

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Reverter migração
python manage.py migrate app_name 0001_previous_migration

# Acessar shell do Django
python manage.py shell

# Executar testes
python manage.py test

# Limpar sessões expiradas
python manage.py clearsessions

# Criar superusuário
python manage.py createsuperuser
```

### 11.2 Troubleshooting Comum

#### **Erro: "relation does not exist"**

```bash
# Solução: Executar migrations
python manage.py migrate
```

#### **Erro: "CORS header 'Access-Control-Allow-Origin' missing"**

```python
# settings.py - Adicionar frontend URL
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://seudominio.ao"
]
```

#### **Erro: "JWT token expired"**

```javascript
// Frontend: Implementar refresh automático
if (response.status === 401) {
    const newToken = await refreshToken();
    // Tentar novamente com novo token
}
```

#### **Erro: "Too many connections" (PostgreSQL)**

```python
# settings.py - Limitar conexões
DATABASES['default']['CONN_MAX_AGE'] = 0  # Desabilitar persistent connections
```

#### **Performance lenta em queries**

```bash
# Ativar query logging
# settings.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        }
    }
}

# Analisar queries no Django Debug Toolbar
pip install django-debug-toolbar
```

### 11.3 Monitoramento de Performance

```python
# Middleware customizado para medir tempo de resposta
import time
from django.utils.deprecation import MiddlewareMixin

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Response-Time'] = f"{duration:.3f}s"
        return response
```

### 11.4 Scripts de Manutenção

```python
# management/commands/cleanup_old_carts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.cart.models import Cart

class Command(BaseCommand):
    help = 'Remove carrinhos antigos (30+ dias sem atividade)'
    
    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=30)
        old_carts = Cart.objects.filter(
            updated_at__lt=cutoff_date,
            user__isnull=True  # Apenas carrinhos anônimos
        )
        
        count = old_carts.count()
        old_carts.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Removidos {count} carrinhos antigos')
        )
```

**Executar:**

```bash
python manage.py cleanup_old_carts
```

---

## 12. Boas Práticas e Padrões

### 12.1 Código Limpo

```python
# ❌ Ruim
def f(x, y):
    z = x + y
    if z > 100:
        return True
    else:
        return False

# ✅ Bom
def is_total_above_threshold(price, quantity, threshold=100):
    """Verifica se o total excede o limiar."""
    total = price * quantity
    return total > threshold
```

### 12.2 Docstrings

```python
def create_order(user, cart, shipping_address):
    """
    Cria um novo pedido a partir do carrinho do usuário.
    
    Args:
        user (CustomUser): Usuário que está fazendo o pedido
        cart (Cart): Carrinho com os itens
        shipping_address (str): Endereço de entrega
    
    Returns:
        tuple: (Order, bool) - Pedido criado e sucesso do pagamento
    
    Raises:
        ValidationError: Se o carrinho estiver vazio
        InsufficientStockError: Se não houver estoque suficiente
    """
    ...
```

### 12.3 Type Hints

```python
from typing import List, Optional, Tuple
from decimal import Decimal

def calculate_order_total(items: List[OrderItem]) -> Decimal:
    """Calcula o total do pedido."""
    total: Decimal = Decimal('0.00')
    for item in items:
        total += item.price * item.quantity
    return total

def get_product_by_slug(slug: str) -> Optional[Product]:
    """Retorna produto pelo slug ou None."""
    try:
        return Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return None
```

### 12.4 Tests

```python
# tests/test_cart.py
from django.test import TestCase
from apps.cart.models import Cart, CartItem
from apps.products.models import Product

class CartTestCase(TestCase):
    def setUp(self):
        """Configuração executada antes de cada teste."""
        self.product = Product.objects.create(
            name="Test Product",
            price=10.00,
            stock_quantity=10
        )
        self.cart = Cart.objects.create(cart_code="TEST123")
    
    def test_add_item_to_cart(self):
        """Testa adição de item ao carrinho."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        self.assertEqual(self.cart.cartitems.count(), 1)
        self.assertEqual(item.quantity, 2)
    
    def test_cart_total(self):
        """Testa cálculo do total do carrinho."""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        
        total = sum(
            item.quantity * item.product.price 
            for item in self.cart.cartitems.all()
        )
        
        self.assertEqual(total, 30.00)
```

### 12.5 Git Workflow

```bash
# Branch para cada feature
git checkout -b feature/add-payment-method

# Commits descritivos
git commit -m "feat: adicionar método de pagamento via cartão"
git commit -m "fix: corrigir validação de estoque em pedidos"
git commit -m "docs: atualizar README com instruções de deploy"

# Prefixos recomendados:
# feat: nova funcionalidade
# fix: correção de bug
# docs: documentação
# style: formatação, ponto e vírgula, etc
# refactor: refatoração de código
# test: adição ou correção de testes
# chore: tarefas de manutenção
```

---

## 13. Glossário de Termos

- **JWT**: JSON Web Token - Token de autenticação
- **ORM**: Object-Relational Mapping - Mapeamento objeto-relacional
- **Serializer**: Converte modelos Django em JSON
- **ViewSet**: Conjunto de views para CRUD
- **Middleware**: Camada de processamento entre request/response
- **Signal**: Sistema de eventos do Django
- **Migration**: Script de alteração do banco de dados
- **Queryset**: Conjunto de registros do banco
- **WSGI**: Web Server Gateway Interface
- **CORS**: Cross-Origin Resource Sharing

---

## 14. Recursos Adicionais

### 14.1 Documentação Oficial

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)

### 14.2 Ferramentas Recomendadas

- **VS Code**: Editor de código
- **Postman**: Teste de APIs
- **pgAdmin**: Administração PostgreSQL
- **Redis Commander**: UI para Redis
- **Docker**: Containerização

### 14.3 Bibliotecas Úteis

```bash
# Imagens
pip install Pillow

# Excel/CSV
pip install openpyxl pandas

# PDF
pip install reportlab

# Celery (tarefas assíncronas)
pip install celery

# Django Debug Toolbar
pip install django-debug-toolbar

# Django Extensions
pip install django-extensions
```

---

## 15. Conclusão

Este manual cobre todos os aspectos técnicos do sistema de e-commerce, desde a arquitetura básica até deploy em produção. Para questões específicas ou problemas não documentados, consulte:

1. Documentação oficial do Django
2. Logs do sistema (`/var/log/`)
3. Swagger UI da API (`/api/docs/`)
4. Equipe de desenvolvimento

**Última atualização:** Novembro 2024  
**Versão do manual:** 1.0  
**Versão da API:** 1.0.0

---

**Desenvolvido com ❤️ para o mercado angolano**
