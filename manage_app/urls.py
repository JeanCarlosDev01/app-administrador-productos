from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('signup', signup, name='signup'),
    path('logout', close_session, name='logout'),
    path('dashboard', index_dashboard, name='dashboard'),
    path('dashboard/account-settings', account_settings, name='account-settings'),
    path('dashboard/change-password', changue_password, name='change-password'),
    path('dashboard/add-product', create_new_product, name='add-product'),
    path('dashboard/add-category', add_category, name='add-category'),
    path('dashboard/product-list', get_products, name='product-list'),
    path('dashboard/product-delete/<int:id>', delete_product, name='product-delete'),
    path('dashboard/product-edit/<int:id>', edit_product, name='product-edit'),
    path('dashboard/product-details/<int:id>', product_details, name='product-details'),
    path('dashboard/product-search/', search_product, name='product-search')
]
