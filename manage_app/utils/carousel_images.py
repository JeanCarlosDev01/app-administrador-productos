def get_carousel_image_list(image_list):
    if len(image_list) == 0:
        act_image = False
        image_list = False
    elif len(image_list) == 1:
        act_image = image_list[0]
    else:
        act_image = image_list[0]
        image_list.pop(0)
    return act_image, image_list