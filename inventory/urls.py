from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Stock URLs
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/add/', views.stock_entry_create, name='stock_entry_create'),
    path('stock/adjust/', views.stock_adjustment_create, name='stock_adjustment_create'),
    
    # Transfer URLs
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/add/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/update/', views.transfer_update, name='transfer_update'),
]
