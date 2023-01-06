from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Cart, Collection, Customer, Order, OrderItem, Product, ProductImage, Reviews,CartItem
class CollectionSerieliziers(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id,**validated_data)

class ProductSerializers(serializers.ModelSerializer):
    images = ProductImageSerializer(many= True)
    class Meta:
        model = Product
        fields = ['id','title','price_with_tax','unit_price','collection','inventory','images']
  
    price_with_tax = serializers.SerializerMethodField(method_name='calculate')
    def calculate(self , product:Product):
        return product.unit_price * 5

class ProductSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','price_with_tax','unit_price']
  
    price_with_tax = serializers.SerializerMethodField(method_name='calculate')
    def calculate(self , product:Product):
        return product.unit_price * 5


class ReviwsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id','name','description','date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Reviews.objects.create(product_id=product_id,**validated_data)

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']

    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product Does Not exist')
        return value
    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
       
        try:
            cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            self.instance=CartItem.objects.create(cart_id=cart_id,**self.validated_data)
        return self.instance



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializers()
    total_prices = serializers.SerializerMethodField('total_price')
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_prices']    
   
    def total_price(self,cartitem:CartItem):
        return cartitem.quantity * cartitem.product.unit_price

    
    

class UpdateCartItemSeializer(serializers.ModelSerializer):
    class Meta:
         model = CartItem
         fields = ['quantity']

    
class CartSerializer(serializers.ModelSerializer): 
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only = True)
    total_of= serializers.SerializerMethodField('total')
    class Meta:
       
        model = Cart
        fields  = ['id','items','total_of']

    def total(self, cart:Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])



class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only = True)
    class Meta:
        model = Customer
        fields= ['id','user_id','birth_date','phone','membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializers()
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price']

class OrderSerializer (serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','placed_at','payment_status','customer','items']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart doesn't exist")
        if CartItem.objects.filter(cart_id=cart_id).count()==0:
            raise serializers.ValidationError('This cart is empty')
        return cart_id

    with transaction.atomic():
        def save(self, **kwargs):
            cart_id=self.validated_data['cart_id']

            customer_id = Customer.objects.get(user_id = self.context['user_id'])

            order=Order.objects.create(customer=customer_id)
            cartitem=CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)

            order_items = [ OrderItem (
                order = order,
                product=item.product,
                unit_price = item.product.unit_price,
                quantity = item.quantity
            ) for item in cartitem]
            OrderItem.objects.bulk_create(order_items)
            CartItem.objects.filter(pk=cart_id).delete()
            return order

