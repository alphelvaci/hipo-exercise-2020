
def calculate_page_params(recipe_count, page):
    if recipe_count % 3 == 0:
        last_page = recipe_count // 3
    else:
        last_page = (recipe_count // 3) + 1

    if page - 1 < 1:
        prev_page = 1
    else:
        prev_page = page - 1
    if page + 1 > last_page:
        next_page = last_page
    else:
        next_page = page + 1

    if page - 3 < 1:
        range_start = 1
    else:
        range_start = page - 3
    if page + 4 > last_page:
        range_end = last_page + 1
    else:
        range_end = page + 4
    page_range = range(range_start, range_end)

    return {
        'prev_page': prev_page,
        'next_page': next_page,
        'last_page': last_page,
        'page_range': page_range,
    }
