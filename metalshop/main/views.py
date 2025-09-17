from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.core.paginator import Paginator
from cart.forms import CartAddProductForm


# Create your views here.

def popular_list(request):
    products = Product.objects.filter(available=True)[:3]
    return render(request, 'main/index/index.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    cart_product_form = CartAddProductForm
    return render(request, 'main/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})


def products_list(request, cat_slug=None):
    cat = None
    cats = Category.objects.all()
    products = Product.objects.filter(available=True)

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 3)
    current_page = paginator.page(int(page))

    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        products = products.filter(category=cat)
        paginator = Paginator(products.filter(category=cat), 3)
        current_page = paginator.page(int(page))
    return render(request, 'main/product/shop.html',
                  {'category': cat, 'categories': cats, 'products': current_page, 'cat_slug': cat_slug})
