from django.shortcuts import render, redirect
from django.contrib import messages
from manage_app.utils import get_max_min_price, get_product_details, search_products

from manage_app.models import Category, Product
from store.utils import get_first_image
from .utils.products_by_category import products_by_category

from manage_app.text import texts


def index(request):
    product_list = Product.objects.order_by('create_date').values()[:3]
    product_list = get_first_image.get_first_product_image(product_list)
    
    context = {
        'categories' : products_by_category(),
        'product_list': product_list
    }
    return render(request, 'index.html', context)
    
def product_info(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO,
                            texts.ERROR_PRODUCT_ID)
        return redirect('catalog')

    context = get_product_details.get_product_details(id)
    return render(request, 'product_info.html', context)

def search_product(request, category=None):
    if category != None:
        products = list(Product.objects.filter(category_id=category).values())
        products = get_first_image.get_first_product_image(products)

    product_list = Product.objects.all()
    
    template_name = 'catalog.html'
    
    try:
        categories = Category.objects.all().values()
        range_min, range_max = get_max_min_price.min_max_price(product_list)
    except:
        messages.add_message(request, messages.INFO, texts.NO_PRODUCTS_REGISTERED)
        return render(request, template_name)
    
    context = {
            'categories': categories,
            'range_min': range_min,
            'range_max': range_max,
        }   
    
    if request.method == 'GET':
        context['product_list'] = products
        return render(request, template_name, context)
    
    try:
        req_min_price = int(request.POST['min-price'])
        req_max_price = int(request.POST['max-price'])
        req_category = request.POST['category']
    except:
        req_min_price = range_min['min'] if range_min['min'] is not None else 0
        req_max_price = range_max['max'] if range_max['max'] is not None else 0
        req_category = '0'
        
    products = search_products.search_products(product_list, req_min_price, req_max_price, req_category, request.POST['input-search'])
    
    products = get_first_image.get_first_product_image(products)

    if len(products) == 0:
        messages.add_message(request, messages.INFO, texts.PRODUCT_NOT_FOUND)
        return render(request, template_name, context)
    
    context['product_list'] = products
    return render(request, template_name, context)