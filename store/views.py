from telnetlib import STATUS
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Cart, CartItem, Collection, Customer, Order, Product, ProductImage, Reviews
from rest_framework import generics

from store.permissions import IsAdminOrReadOnly
from .seializers import ProductImageSerializer, AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerieliziers, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializers, ProductSimpleSerializers, ReviwsSerializers, UpdateCartItemSeializer
from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import Count


# Create your views here.
class ProductViewset(ModelViewSet):

    serializer_class = ProductSerializers
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('images').all()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id is not None:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class CartViewset(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CollectionViewset(ModelViewSet):
    queryset = Collection.objects.annotate(
        product_count=Count('product')).all()
    serializer_class = CollectionSerieliziers
    permission_classes = [IsAdminOrReadOnly]


class ReviewsViewset(ModelViewSet):

    serializer_class = ReviwsSerializers

    def get_queryset(self):
        return Reviews.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartItemViewset(ModelViewSet):
    http_method_names = ['patch', 'get', 'post', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSeializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewset(ModelViewSet):
       queryset = Customer.objects.all()
       serializer_class = CustomerSerializer
       permission_classes = [IsAdminUser]

       @action(detail=False,methods=['GET','POST'],permission_classes=[IsAuthenticated])
       def me (self,request):
        customer=Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET': 
         serializer = CustomerSerializer(customer)
         return Response(serializer.data)
        elif request.method == 'POST':
          serializer = CustomerSerializer(customer, data = request.data)
          serializer.is_valid()
          serializer.save
          return Response(serializer.data)


class OrderViewset(ModelViewSet):
    
   
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data = request.data,context = {'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializers = OrderSerializer(order)
        return Response(serializers.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

class ProductImageViewset(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])