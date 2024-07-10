
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import OrderItem, Product, Collection, Review
from .serializers import ProductSerializer,CollectionSerializer, ReviewSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
