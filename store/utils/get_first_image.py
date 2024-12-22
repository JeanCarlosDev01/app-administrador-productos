from manage_app.models import ProductImages

def get_first_product_image(product_list):
    for product in product_list:
        image = ProductImages.objects.filter(product_id=product['id']).first()
        if image is None:
            product['image'] = 'https://salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled-1150x647.png'
        else:
            product['image'] = image.url
    return product_list