from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as user_session, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage

from manage_app.utils import get_max_min_price, get_product_details

from .utils.search_products import search_products
from store.utils.products_by_category import products_by_category

from .models import *

from .utils.join_urls import join_urls
from .templatetags.format_price import format_price

from .text import texts
# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    template_title = {'title': 'Iniciar sessíon'}
    template_url = 'auth/login.html'
    
    if request.method == 'POST':
        user_email = request.POST['useremail']
        user_password = request.POST['password']
        try:
            user = User.objects.get(email=user_email)
            if user.check_password(user_password):
                user_session(request, user)
                return redirect('dashboard')
            else:
                messages.add_message(request, messages.ERROR, texts.ERROR_PASSWORD)
                return render(request,template_url)
        except:
            messages.add_message(request, messages.ERROR, texts.USER_NOT_FOUND)
            return render(request, template_url)
        
    return render(request, template_url, template_title)


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    template_title = {'title': 'Registrarse'}
    template_url = 'auth/signup.html'
    
    if request.method == 'POST':
        user_name = request.POST['username']
        user_email = request.POST['email']
        user_password = request.POST['password']
        try:
            User.objects.get(email=user_email)
            messages.add_message(request, messages.ERROR, texts.EMAIL_IS_ALREADY_IN_USE)
            return render(request, template_url, template_title)
        except:
            try:
                user = User.objects.create_user(
                    username=user_name,
                    email=user_email,
                    password=user_password
                )
                user_session(request, user)
                return redirect('dashboard')
            except IntegrityError:
                messages.add_message(request, messages.ERROR, texts.USERNAME_IS_ALREADY_IN_USE)
                return render(request,template_url, template_title)
    
    return render(request, template_url, template_title)


@login_required(login_url='login')
def close_session(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index_dashboard(request):
    active_user = request.user
    user_products = Product.objects.filter(user_id=active_user)
    total_products = user_products.count()
    
    price_range = get_max_min_price.min_max_price(user_products)

    min_price_format = price_range[0]['min'] if price_range else 0
    max_price_format = price_range[1]['max'] if price_range else 0
    
    categories_data = products_by_category()
        
    context = {'title': f'{request.user} | Dashboard',
                'username': request.user,
                'total_products': total_products,
                'min_price': min_price_format,
                'max_price': max_price_format,
                'categories': categories_data
                }
    
    return render(request, 'account/user_statistics.html', context)

@login_required(login_url='login')
def account_settings(request):
    user = User.objects.get(id=request.user.id)
    
    if request.method == 'POST':
        user.username = request.POST['username']
        user.first_name = request.POST['firstname']
        user.last_name = request.POST['lastname']
        user.save()
        return redirect('dashboard')

    context = {
        'user' : user
    }

    return render(request, 'account/account_settings.html', context)


@login_required(login_url='login')
@require_http_methods(['POST'])
def changue_password(request):
    user = User.objects.get(id=request.user.id)

    user.set_password(request.POST['password'])
    user.save()
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def create_new_product(request):
    categories = Category.objects.all().values()
    if len(categories) == 0:
        categories = [{'id': 0, 'name': texts.NO_CATEGORIES_FOUND}]

    context = {'categories': categories}
    template_url = 'account/add_product.html'
    
    if request.method == 'POST':
        message = texts.PRODUCT_SUCCESSFULLY_REGISTERED
        
        try:
            category = Category.objects.get(id=int(request.POST['category']))
            new_product = Product.objects.create(
                name=request.POST['name'],
                category=category,
                stock=int(request.POST['stock']),
                price=int(request.POST['price']),
                user=request.user
            )

            url_images = request.POST['images'].split(',')
            for url in url_images:
                if url != '':
                    ProductImages.objects.create(url=url, product=new_product)

            try:
                Description.objects.create(description=request.POST['description'], product=new_product)
            except:
                Description.objects.create(description=texts.DEFAULT_PRODUCT_DESCRIPTION, product=new_product)
                message = texts.ERROR_ADDING_DESCRIPTIION
            
            messages.add_message(request, messages.INFO, message)
            return render(request, template_url, context)
        except:
            messages.add_message(
                request, messages.INFO, texts.ERROR_PRODUCT_NO_REGISTERED)
            return render(request, template_url, context)

    return render(request, template_url, context)


@login_required(login_url='login')
@require_http_methods(['POST'])
def add_category(request):
    try:
        Category.objects.create(name=request.POST['category'])
        messages.add_message(request, messages.INFO, texts.SUCCESSFULLY_CREATED_CATEGORY)
        return redirect('add-product')
    except:
        messages.add_message(request, messages.INFO, texts.ERROR_NO_CATEGORY_CREATED)
        return redirect('add-product')


@login_required(login_url='login')
@require_http_methods(['GET'])
def get_products(request):
    template_url = 'account/product_list.html'
    try:
        product_list = list(Product.objects.filter(user=request.user))
        page = request.GET.get('page', 1)
        paginator = Paginator(product_list, 10)
        product_list = paginator.page(page)
        
        context = {
            'product_list': product_list,
            'paginator': paginator
        }
        
        return render(request, template_url, context)
    except:
        messages.add_message(request, messages.INFO, texts.PRODUCTS_NOT_FOUND)
        return render(request, template_url)


@login_required(login_url='login')
def delete_product(request, id):
    try:
        Product.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, texts.PRODUCT_SUCCESSFULLY_REMOVED)
    except:
        messages.add_message(request, messages.INFO, texts.PRODUCT_NOT_FOUND)

    return redirect('product-list')


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def edit_product(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO, texts.ERROR_PRODUCT_ID)
        return redirect('product-list')
    
    try:
        product = Product.objects.get(id=id)
        categories = Category.objects.all()
        images = ProductImages.objects.filter(product_id=id)
        description = Description.objects.get(product_id=id)
    except:
        messages.add_message(request, messages.INFO,
                            texts.ERROR_LOADING_PRODUCT)
        return redirect('product-list')
        
    if request.method == 'GET':
        return render(request, 'account/edit_product.html', {
            'product': product,
            'categories': categories.values(),
            'description': description,
            'images': images.values(),
            'input_imgs': join_urls(images.values())
        })

    try:
        new_category = Category.objects.get(id=int(request.POST['category']))
        product.name = request.POST['name']
        product.category = new_category
        product.stock = int(request.POST['stock'])
        product.price = int(request.POST['price'])
        product.user = request.user
        product.save()

        images.delete()
        url_images = request.POST['images'].split(',')
        for url in url_images:
            if url != '':
                ProductImages.objects.create(url=url, product=product)

        description.description = request.POST['description']
        description.save()

        messages.add_message(request, messages.INFO, texts.PRODUCT_SUCCESSFULLY_UPDATED)
        return redirect('product-list')
    except:
        messages.add_message(request, messages.INFO, texts.ERROR_UPDATING_PRODUCT)
        return redirect('product-list')

@login_required(login_url='login')
@require_http_methods(['GET'])
def product_details(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO,
                            texts.ERROR_PRODUCT_ID)
        return redirect('product-list')

    context = get_product_details.get_product_details(id)
    return render(request, 'account/details_product.html', context)

@login_required(login_url='login')
def search_product(request):
    active_user = request.user
    user_products = Product.objects.filter(user_id=active_user)
    
    template_url = 'account/search_product.html'
    
    try:
        categories = Category.objects.all().values()
        range_min, range_max = get_max_min_price.min_max_price(user_products)
    except:
        messages.add_message(request, messages.INFO, texts.NO_PRODUCTS_REGISTERED)
        return render(request, template_url)

    context = {
            'categories': categories,
            'range_min': range_min,
            'range_max': range_max
        }

    if request.method == 'POST':
        req_min_price = request.POST.get('min-price')
        req_max_price = request.POST.get('max-price')
        req_category = request.POST.get('category')
        req_input_search = request.POST.get('input-search')
    else:
        req_min_price = range_min['min']
        req_max_price = range_max['max']
        req_category = '0'
        req_input_search = ''

    product_list = search_products(user_products, req_min_price, req_max_price, req_category, req_input_search)
    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 10)
    try:
        product_list = paginator.page(page)
    except EmptyPage:
        product_list = paginator.page(paginator.num_pages)
            
    if len(product_list) == 0:
        messages.add_message(request, messages.INFO, texts.PRODUCTS_NOT_FOUND)
        return render(request, template_url, context)

    context['product_list'] = product_list
    return render(request, template_url, context)