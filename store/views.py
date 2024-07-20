
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from store.filters import ProductFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin
from store.pagination import DefaultPagination
from .models import Cart, OrderItem, Product, Collection, Review
from .serializers import ProductSerializer,CollectionSerializer, ReviewSerializer, CartSerializer
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

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item'})
        return super().destroy(request, *args , **kwargs)
                                    
        
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count= Count("products")).all()
    serializer_class = CollectionSerializer


# Create your views here.

class ReviewViewSet(ModelViewSet):

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']) 
    
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(RetrieveModelMixin, CreateModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer