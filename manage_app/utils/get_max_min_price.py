from django.db.models import Min, Max

def min_max_price(product_list):
    try:
        min_price = product_list.aggregate(Min('price'))['price__min']
        max_price = product_list.aggregate(Max('price'))['price__max']

        range_min = {
            'min': min_price,
            'max': (min_price + max_price) / 2
        }
        range_max = {
            'min': (min_price + max_price) / 2,
            'max': max_price
        }
    except:
        return None
    return range_min, range_max