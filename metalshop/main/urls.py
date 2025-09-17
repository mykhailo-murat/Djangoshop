from django.urls import include, path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.popular_list, name='popular_list', ),
    path('shop/', views.products_list, name='products_list'),
    path('shop/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shop/category/<slug:cat_slug>/', views.products_list, name='products_list_by_cat'),
]
