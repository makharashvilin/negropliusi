from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem
from .forms import ProductForm
from django.contrib import messages
from .utils import  *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    filters =  get_filters(request)
    products = Product.objects.filter(**filters)
    sort_by = request.GET.get('sort')
    if sort_by:
        products = products.order_by(sort_by)


    products_paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = products_paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = products_paginator.page(1)
    except EmptyPage:
        page_obj = products_paginator.page(products_paginator.num_pages)

    categories = Category.objects.all()

    return render(request, 'home.html', {'products': page_obj,
                                                              'products_paginator': products_paginator,
                                                              'categories': categories})

def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    product.views+=1
    product.save()
    return render(request, 'product_detail.html', {'product': product})


def create_product(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Your product has been created successfully.')
            return redirect('home')

    return render(request, 'product_form.html',
                  {'form': form})


def update_product(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Your product has been Updated successfully.')
            return redirect('product_detail', id=id)

    return render(request, 'product_form.html',
                  {'form': form})

def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    messages.add_message(request, messages.SUCCESS, 'Your product has been deleted.')
    return redirect('home')


def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html',{'cart': cart})


def add_product_to_cart(request, id ):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = Product.objects.get(id=id)
    if product.stock_qty < 1:
        messages.error(request, f"Product {product.name} is not available.")
        return redirect('product_detail', id=id)
    cart_item, item_created = CartItem.objects.get_or_create(product=product, cart=cart)
    if item_created:
        cart_item.qty = 1
    else:
        cart_item.qty += 1
    cart_item.save()
    product.stock_qty -= 1
    product.save()
    return redirect('product_detail', id=id)


def delete_cart_item(request, id):
    cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    product = cart_item.product
    product.stock_qty += cart_item.qty
    product.save()
    cart_item.delete()
    return redirect('cart_view')