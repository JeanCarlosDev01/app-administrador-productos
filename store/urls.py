from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('catalog/', search_product, name='search'),
    path('catalog/<int:category>', search_product, name='search-category'),
    path('product/<int:id>', product_info, name='product-info'),
]
