from manage_app.models import Category, Product

class Products_by_Category:
    def __init__(self, category_id, category_name, category_count):
        self.category_id = category_id
        self.category = category_name
        self.number_of_products = category_count

def products_by_category():
    categories = Category.objects.all()
    products_by_category = []
    for category in categories:
        category_count = Product.objects.filter(category_id=category.id).count()
        products_by_category.append(Products_by_Category(category.id ,category.name, category_count))
    return products_by_category