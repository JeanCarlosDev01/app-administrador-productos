from django.db.models import Min, Max
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as user_session, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib import messages

from .models import *

from .utils import *
# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    template_title = {"title": "Iniciar sessíon"}
    template_url = 'auth/login.html'
    
    if request.method == "POST":
        user_email = request.POST["useremail"]
        user_password = request.POST["password"]
        try:
            user = User.objects.get(email=user_email)
            if user.check_password(user_password):
                user_session(request, user)
                return redirect("dashboard")
            else:
                messages.add_message(request, messages.ERROR, 'Contraseña incorrecta')
                return render(request,template_url, {})
        except:
            messages.add_message(request, messages.ERROR, 'No se encontro el usuario')
            return render(request, template_url, {})
        
    return render(request, template_url, template_title)


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    template_title = {"title": "Registrarse"}
    template_url = "auth/signup.html"
    
    if request.method == "POST":
        user_name = request.POST["username"]
        user_email = request.POST["email"]
        user_password = request.POST["password"]
        try:
            User.objects.get(email=user_email)
            messages.add_message(request, messages.ERROR, 'El correo electronico ya esta registrado')
            return render(request, template_url, template_title)
        except:
            try:
                user = User.objects.create_user(
                    username=user_name,
                    email=user_email,
                    password=user_password
                )
                user_session(request, user)
                return redirect("dashboard")
            except IntegrityError:
                messages.add_message(request, messages.ERROR, 'El nombre de usuario no esta disponible')
                return render(request,template_url, template_title)
    
    return render(request, template_url, template_title)


@login_required(login_url="login")
def close_session(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def index_dashboard(request):
    active_user = request.user
    user_products = Product.objects.filter(user_id=active_user)
    total_products = user_products.count()
    min_price = user_products.aggregate(Min('price'))['price__min'] if user_products.aggregate(Min('price'))['price__min'] else 0
    max_price = user_products.aggregate(Max('price'))['price__max'] if user_products.aggregate(Max('price'))['price__max'] else 0
    
    min_price_format = format_price(min_price)
    max_price_format = format_price(max_price)
    
    categories = Category.objects.all()
    categories_data = list()
    for category in categories:
        pr_category = user_products.filter(category_id=category.id).count()
        category_data = {
            'name' : category.name,
            'total_products': pr_category
        }
        categories_data.append(category_data)
        
    context = {'title': f'{request.user} | Dashboard',
                'username': request.user,
                'total_products': total_products,
                'min_price': min_price_format,
                'max_price': max_price_format,
                'categories': categories_data
                }
    
    return render(request, "account/user_statistics.html", context)

@login_required(login_url="login")
def account_settings(request):
    user = User.objects.get(id=request.user.id)
    
    if request.method == "POST":
        user.username = request.POST["username"]
        user.first_name = request.POST["firstname"]
        user.last_name = request.POST["lastname"]
        user.save()
        return redirect("dashboard")

    context = {"username": user.username,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email
                }

    return render(request, "account/account_settings.html", context)


@login_required(login_url="login")
@require_http_methods(["POST"])
def changue_password(request):
    user = User.objects.get(id=request.user.id)

    user.set_password(request.POST["password"])
    user.save()
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def create_new_product(request):
    categories = Category.objects.all().values()
    if len(categories) == 0:
        categories = [{"id": 0, "name": "No hay categorias registradas"}]

    context = {"categories": categories}
    template_url = "account/add_product.html"
    
    if request.method == "POST":
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

            Description.objects.create(description=request.POST['description'], product=new_product)
            
            messages.add_message(request, messages.INFO, 'El producto se registro exitosamente')
            return render(request, template_url, context)
        except:
            messages.add_message(
                request, messages.INFO, 'No se pudo registrar el prodcto, verifica la información')
            return render(request, template_url, context)

    return render(request, template_url, context)


@login_required(login_url="login")
@require_http_methods(["POST"])
def add_category(request):
    try:
        Category.objects.create(name=request.POST["category"])
        messages.add_message(request, messages.INFO, 'Se creo la categoria')
        return redirect("add-product")
    except:
        messages.add_message(request, messages.INFO, 'No se creo la categoria')
        return redirect("add-product")


@login_required(login_url='login')
@require_http_methods(["GET"])
def get_products(request):
    template_url = 'account/product_list.html'
    try:
        product_list = list(Product.objects.filter(user=request.user))
        return render(request, template_url, {'product_list': product_list})
    except:
        messages.add_message(request, messages.INFO, 'No de pudo encontrar los productos')
        return render(request, template_url)


@login_required(login_url='login')
def delete_product(request, id):
    try:
        Product.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, 'Producto eliminado')
    except:
        messages.add_message(request, messages.INFO,'No se encontro el producto')

    return redirect('product-list')


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_product(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO, 'No se identifico el ID el producto')
        return redirect('product-list')
    
    try:
        product = Product.objects.get(id=id)
        categories = Category.objects.all()
        images = ProductImages.objects.filter(product_id=id)
        description = Description.objects.get(product_id=id)
    except:
        messages.add_message(request, messages.INFO,
                            'No se pudo cargar el producto')
        return redirect('product-list')
        
    if request.method == 'GET':
        return render(request, 'account/edit_product.html', {
            'product': product,
            'categories': categories.values(),
            'description': description,
            'images': images.values(),
            'input_imgs': join_urls(images)
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

        messages.add_message(request, messages.INFO, 'El producto se actualizo exitosamente')
        return redirect('product-list')
    except:
        messages.add_message(request, messages.INFO, 'Error al actualizar el producto')
        return redirect('product-list')

@login_required(login_url='login')
@require_http_methods(["GET"])
def product_details(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO,
                            'No se identifico el ID el producto')
        return redirect('product-list')

    product = Product.objects.get(id=id)
    description = Description.objects.get(product_id=product)
    images = list(ProductImages.objects.filter(product_id=product).values())
    
    if len(images) == 0:
        act_image = False
        images = False
    elif len(images) == 1:
        act_image = images[0]
    else:
        act_image = images[0]
        images.pop()  
    
    context = {
        'product': product,
        'product_price': format_price(product.price),
        'description': description,
        'active_image' : act_image,
        'images': images
    }
    return render(request, 'account/details_product.html', context)

@login_required(login_url='login')
def search_product(request):
    active_user = request.user
    user_products = Product.objects.filter(user_id=active_user)
    
    template_url = 'account/search_product.html'
    
    try:
        categories = Category.objects.all().values()
        min_price = user_products.aggregate(Min('price'))['price__min']
        max_price = user_products.aggregate(Max('price'))['price__max']

        range_min = {
            'min': min_price,
            'max': (min_price + max_price) / 2
        }
        range_max = {
            'min': (min_price + max_price) / 2,
            'max': max_price,
        }
    except:
        messages.add_message(request, messages.INFO, 'No hay productos registrados')
        return render(request, template_url)

    context = {
            'categories': categories,
            'range_min': range_min,
            'range_max': range_max
        }

    if request.method == 'GET':
        return render(request, template_url, context)
    
    req_min_price = int(request.POST['min-price'])
    req_max_price = int(request.POST['max-price'])
    req_category = request.POST['category']
    req_input_search = request.POST['input-search']
    
    products = user_products.filter(price__range=(req_min_price, req_max_price))
    
    if req_category != '0':
        products = products.filter(category_id=req_category)
        
    if req_input_search != '':
        try:
            products = products.filter(id=int(req_input_search))
        except:
            products = products.filter(name__icontains=req_input_search)
        
    if len(products) == 0:
        messages.add_message(request, messages.INFO, 'No se encontraron productos')
        return render(request, template_url, context)

    context['product_list'] = products
    return render(request, template_url, context)