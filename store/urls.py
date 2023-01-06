from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()

router.register('product',views.ProductViewset,basename='product')
router.register('collection',views.CollectionViewset)
router.register('cart',views.CartViewset)
router.register('customer',views.CustomerViewset)
router.register('order',views.OrderViewset,basename='order')


domains_router = routers.NestedSimpleRouter(router, 'product', lookup='product')
domains_router.register('reviews', views.ReviewsViewset, basename='product-reviews')
domains_router.register('images', views.ProductImageViewset, basename='product-images')
domains_cart = routers.NestedSimpleRouter(router, 'cart', lookup='cart')
domains_cart.register('items', views.CartItemViewset, basename='cart-items')
# URLConf
urlpatterns = [
    path('', include(router.urls)),
    path('', include(domains_router.urls)),
    path('', include(domains_cart.urls)),
]