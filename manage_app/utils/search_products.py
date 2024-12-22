def search_products(product_list, min_price: int, max_price: int, category: int, input_search: str):    
    products = product_list.filter(price__range=(min_price, max_price))
    
    if category != '0':
        products = products.filter(category_id=category)
        
    if input_search != '':
        try:
            products = products.filter(id=int(input_search))
        except:
            products = products.filter(name__icontains=input_search)
    
    return products.values()