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

    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST["username"])
            if user.check_password(request.POST["password"]):
                user_session(request, user)
                return redirect("dashboard")
            else:
                return render(
                    request,
                    "auth/login.html",
                    {"title": "Iniciar sessíon", "error": "Contraseña incorrecta"},
                )
        except:
            return render(
                request,
                "auth/login.html",
                {"title": "Iniciar sessíon", "error": "No se encontro el usuario"},
            )
    else:
        return render(
            request,
            "auth/login.html",
            {
                "title": "Iniciar sessíon",
            },
        )


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        try:
            User.objects.get(email=request.POST["email"])
            return render(
                request,
                "auth/signup.html",
                {
                    "title": "Registrarse",
                    "error": "El correo electronico ya esta registrado",
                },
            )
        except:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"],
                    email=request.POST["email"],
                    password=request.POST["password"],
                )
                user.save()
                user_session(request, user)
                return redirect("dashboard")
            except IntegrityError:
                return render(
                    request,
                    "auth/signup.html",
                    {
                        "title": "Registrarse",
                        "error": "El nombre de usuario no esta disponible",
                    },
                )
    else:
        return render(request, "auth/signup.html", {"title": "Registrarse"})


@login_required(login_url="login")
def close_session(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def index_dashboard(request):

    total_products = Product.objects.filter(user_id=request.user).count()
    min_price = Product.objects.filter(user_id=request.user).aggregate(Min('price'))
    max_price = Product.objects.filter(user_id=request.user).aggregate(Max('price'))
    
    try:
        min_price_format = format_price(min_price['price__min'])
        max_price_format = format_price(max_price['price__max'])
    except:
        min_price_format = 0
        max_price_format = 0
    
    categories = Category.objects.all()
    categories_data = list()
    for category in categories:
        pr_category = Product.objects.filter(category_id=category.id, user_id=request.user).count()
        data = {
            'name' : category.name,
            'total_products' : pr_category
        }
        categories_data.append(data)
        
    return render(request, "account/user_statistics.html", 
                    {"title": f"{request.user} | Dashboard",
                    "username": request.user,
                    'total_products' : total_products,
                    'min_price' : min_price_format,
                    'max_price' : max_price_format,
                    'categories' : categories_data
                    })


@login_required(login_url="login")
def account_settings(request):
    try:
        user = User.objects.get(id=request.user.id)
    except:
        return HttpResponse("<h1>NO SE ENCONTRO EL USUARIO<h2>")

    if request.method == "POST":
        user.username = request.POST["username"]
        user.first_name = request.POST["firstname"]
        user.last_name = request.POST["lastname"]
        user.save()
        return redirect("dashboard")

    return render(
        request,
        "account/account_settings.html",
        {
            "username": user.username,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "email": user.email,
        },
    )


@login_required(login_url="login")
@require_http_methods(["POST"])
def changue_password(request):
    try:
        user = User.objects.get(id=request.user.id)
    except:
        return HttpResponse("<h1>NO SE ENCONTRO EL USUARIO<h2>")

    user.set_password(request.POST["password"])
    user.save()
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def create_new_product(request):
    categories = Category.objects.all().values()
    if len(categories) == 0:
        categories = [{"id": 0, "name": "No hay categorias registradas"}]

    if request.method == "POST":
        try:
            category = Category.objects.get(id=int(request.POST['category']))
            new_product = Product(
                name=request.POST['name'],
                category=category,
                stock=int(request.POST['stock']),
                price=(request.POST['price']),
                user=request.user
            )
            new_product.save()

            url_images = request.POST['images'].split(',')
            for url in url_images:
                if url != '':
                    product_image = ProductImages(
                        url=url,
                        product=new_product)
                    product_image.save()

            product_description = Description(
                description=request.POST['description'],
                product=new_product
            )
            product_description.save()

            messages.add_message(request, messages.INFO,
                                 'El producto se registro exitosamente')
            return render(request, "account/add_product.html", {"categories": categories})
        except:
            messages.add_message(
                request, messages.INFO, 'No se pudo registrar el prodcto, verifica la información')
            return render(request, "account/add_product.html", {"categories": categories})

    return render(request, "account/add_product.html", {"categories": categories})


@login_required(login_url="login")
@require_http_methods(["POST"])
def add_category(request):
    try:
        new_category = Category(name=request.POST["category"])
        new_category.save()
        messages.add_message(request, messages.INFO, 'Se creo la categoria')
        return redirect("add-product")
    except:
        messages.add_message(request, messages.INFO, 'No se creo la categoria')
        return redirect("add-product")


@login_required(login_url='login')
@require_http_methods(["GET"])
def get_products(request):
    try:
        product_list = list(Product.objects.filter(user=request.user.id))
        return render(request, 'account/product_list.html', {'product_list': product_list})
    except:
        messages.add_message(request, messages.INFO,
                             'No de pudo encontrar los productos')
        return render(request, 'account/product_list.html')


@login_required(login_url='login')
def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
        product.delete()
        messages.add_message(request, messages.INFO, 'Producto eliminado')
    except:
        messages.add_message(request, messages.INFO,
                             'No se encontro el producto')

    return redirect('product-list')


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_product(request, id=None):
    if id is None:
        messages.add_message(request, messages.INFO,
                            'No se identifico el ID el producto')
        return redirect('product-list')

    if request.method == 'GET':
        try:
            product = Product.objects.get(id=id)
            categories = Category.objects.all().values()
            images = ProductImages.objects.filter(product_id=id).values()
            description = Description.objects.get(product_id=id)

            return render(request, 'account/edit_product.html', {
                'product': product,
                'categories': categories,
                'description': description,
                'images': images,
                'input_imgs': join_urls(images)
            })
        except:
            messages.add_message(request, messages.INFO,
                                'No se pudo cargar el producto')
            return redirect('product-list')

    try:
        new_category = Category.objects.get(id=int(request.POST['category']))
        product = Product.objects.get(id=id)
        product.name = request.POST['name']
        product.category = new_category
        product.stock = int(request.POST['stock'])
        product.price = int(request.POST['price'])
        product.user = request.user
        product.save()

        images = ProductImages.objects.filter(product_id=product.id).delete()
        url_images = request.POST['images'].split(',')
        for url in url_images:
            if url != '':
                product_image = ProductImages(
                    url=url,
                    product=product)
                product_image.save()

        description = Description.objects.get(product_id=product.id)
        description.description = request.POST['description']
        description.save()

        messages.add_message(request, messages.INFO,
                             'El producto se actualizo exitosamente')
        return redirect('product-list')
    except:
        messages.add_message(request, messages.INFO,
                             'Error al actualizar el producto')
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
    
    if len(images) <= 0:
        act_image = False
        images = False
    else:
        act_image = images[0]
        images.pop(0)
    
    

    return render(request, 'account/details_product.html', {
        'product': product,
        'product_price': format_price(product.price),
        'description': description,
        'active_image' : act_image,
        'images': images
    })


@login_required(login_url='login')
def search_product(request):
    try:
        categories = Category.objects.all().values()

        min_price = Product.objects.filter(
            user_id=request.user).aggregate(Min('price'))
        max_price = Product.objects.filter(
            user_id=request.user).aggregate(Max('price'))

        range_min = {
            'min': min_price['price__min'],
            'max': (min_price['price__min'] + max_price['price__max']) / 2
        }
        range_max = {
            'min': (min_price['price__min'] + max_price['price__max']) / 2,
            'max': max_price['price__max'],
        }
    except:
        messages.add_message(request, messages.INFO, 'No hay productos registrados')
        return render(request, 'account/search_product.html')

    if request.method == 'GET':
        return render(request, 'account/search_product.html', {
            'categories': categories,
            'range_min': range_min,
            'range_max': range_max
        })
    
    req_min_price = int(request.POST['min-price'])
    req_max_price = int(request.POST['max-price'])
    req_category = request.POST['category']
    req_input_search = request.POST['input-search']
    
    user_products = Product.objects.filter(user_id=request.user)
    
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
        return render(request, 'account/search_product.html', {
            'categories': categories,
            'range_min': range_min,
            'range_max': range_max,
    })

    return render(request, 'account/search_product.html', {
        'categories': categories,
        'range_min': range_min,
        'range_max': range_max,
        'product_list' : products
    })