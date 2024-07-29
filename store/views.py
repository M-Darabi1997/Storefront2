
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from store.filters import ProductFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin, UpdateModelMixin
from store.pagination import DefaultPagination
from store.permissions import IsAdminOrReadOnly
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review
from .serializers import AddCartItemSerializer, CustomerSerializer, OrderSerializer, ProductSerializer,CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, UpdateCartItemSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet,GenericViewSet


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter ]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item'})
        return super().destroy(request, *args , **kwargs)
                                    
        
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count= Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

# Create your views here.

class ReviewViewSet(ModelViewSet):

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']) 
    
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(RetrieveModelMixin, DestroyModelMixin, CreateModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs["cart_pk"]}
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer


    def get_queryset(self):
        return CartItem.objects\
            .filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')
    
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

  

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
        
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class OrderViewSet(ModelViewSet):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        (customer_id, created) = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)