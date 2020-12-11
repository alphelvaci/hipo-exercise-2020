from django.shortcuts import render
from django.http import HttpResponse
from .models import Ingredient, Recipe
from django.db.models import Count

def index(request):
    #get the html GET parameters
    try:
        page = int(request.GET['page'])
    except:
        page = 1
    try:
        filter_ingredient = request.GET['ingredient']
        filtered = True
    except:
        filter_ingredient = None
        filtered = False
    try:
        search = int(request.GET['search'])
        searched = True
    except:
        search = None

    if filtered:
        recipes = Recipe.objects.filter(ingredients__name=filter_ingredient).order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.filter(ingredients__name=filter_ingredient).count()
    else:
        recipes = Recipe.objects.order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.count()
    ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
    for recipe in recipes:
        recipe.instructions = recipe.instructions.split('\r\n')

    if recipe_count%3 == 0:
        last_page = recipe_count//3
    else:
        last_page = (recipe_count//3)+1

    if page-1 < 1:
        prev_page = 1
    else:
        prev_page = page-1
    if page+1 > last_page:
        next_page = last_page
    else:
        next_page = page+1

    if page-3 < 1:
        range_start = 1
    else:
        range_start = page+5
    if page+5 > last_page:
        range_end = last_page+1
    else:
        range_end = page-3
    page_range = range(range_start, range_end)

    return render(request, 'recipes/index.html',
    {'recipes': recipes, 'ingredients': ingredients, 'page': page,
    'page_range': page_range, 'prev_page': prev_page, 'next_page': next_page,
    'last_page': last_page, 'filter_ingredient': filter_ingredient})