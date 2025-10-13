from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductListSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    # Filter by store if provided
    store_slug = request.query_params.get("store", None)
    if store_slug:
        products = Product.objects.filter(store__slug=store_slug, store__is_active=True)
    else:
        products = Product.objects.filter(feature=True, store__is_active=True)
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)
