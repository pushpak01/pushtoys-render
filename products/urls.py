from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product listing and search
    path('', views.product_list, name='list'),
    path('search/', views.product_list, name='search'),
    path('category/<slug:category_slug>/', views.product_list, name='by_category'),

    # Product detail views (with and without slug)
    path('product/<int:pk>/', views.product_detail, name='detail'),
    path('product/<int:pk>/<slug:slug>/', views.product_detail, name='detail_with_slug'),
]