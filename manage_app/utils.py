def format_price(price):
    return f"{price:,}".replace(",", ".")

def join_urls(list):
    concat_url = ''
    for image in list:
        concat_url += f'{image['url']},'
    return concat_url