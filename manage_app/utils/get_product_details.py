from manage_app.models import Product, Description, ProductImages
from manage_app.utils.carousel_images import get_carousel_image_list

def get_product_details(id):
    product = Product.objects.get(id=id)
    
    description = Description.objects.get(product_id=product).description

        
    images = list(ProductImages.objects.filter(product_id=product).values())
    
    act_image, images = get_carousel_image_list(images)

    product_data = {
        'product': product,
        'description': description,
        'active_image': act_image,
        'images': images
    }
    
    return product_data