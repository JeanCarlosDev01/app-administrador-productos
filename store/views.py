from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Min, Max
from manage_app.utils import format_price

from manage_app.models import Category, Product, ProductImages, Description

def index(request):
    categories = Category.objects.all().values()
        
    return render(request, 'index.html', {
        'categories' : categories
    })
    
def product_info(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO,
                            'No se identifico el ID el producto')
        return redirect('catalog')

    product = Product.objects.get(id=id)
    
    description = Description.objects.get(product_id=product).description

        
    images = list(ProductImages.objects.filter(product_id=product).values())
    
    if len(images) == 0:
        act_image = False
        images = False
    elif len(images) == 1:
        act_image = images[0]
    else:
        act_image = images[0]
        images.pop(0)    

    context = {
        'product': product,
        'product_price': format_price(product.price),
        'description': description,
        'active_image' : act_image,
        'images': images
    }

    return render(request, 'product_info.html', context)

def search_product(request, category=None):
    if category != None:
        products = list(Product.objects.filter(category_id=category).values())
        for product in products:
            image = ProductImages.objects.filter(product_id=product['id']).first()
            if image is None:
                product['image'] = 'https://salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled-1150x647.png'
            else:
                product['image'] = image.url

    template_name = 'catalog.html'
    
    try:
        categories = Category.objects.all().values()
        
        min_price = Product.objects.aggregate(Min('price'))['price__min']
        max_price = Product.objects.aggregate(Max('price'))['price__max']

        range_min = {
            'min': min_price,
            'max': (min_price + max_price) / 2
        }
        range_max = {
            'min': (min_price + max_price) / 2,
            'max': max_price
        }
    except:
        messages.add_message(request, messages.INFO, 'No hay productos registrados')
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
        req_min_price = min_price
        req_max_price = max_price
        req_category = '0'
    
    req_input_search = request.POST['input-search']
    
    products = Product.objects.filter(price__range=(req_min_price, req_max_price))
    
    if req_category != '0':
        products = products.filter(category_id=req_category)
        
    if req_input_search != '':
        try:
            products = products.filter(id=int(req_input_search))
        except:
            products = products.filter(name__icontains=req_input_search)
    
    products = list(products.values())
    
    for product in products:
        image = ProductImages.objects.filter(product_id=product['id']).first()
        if image is None:
            product['image'] = 'https://salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled-1150x647.png'
        else:
            product['image'] = image.url

    if len(products) == 0:
        messages.add_message(request, messages.INFO, 'No se encontraron productos')
        return render(request, template_name, context)
    
    context['product_list'] = products
    return render(request, template_name, context)