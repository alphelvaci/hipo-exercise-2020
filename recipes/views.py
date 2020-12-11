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
        ingredient = int(request.GET['ingredient'])
    except:
        ingredient = None
    try:
        search = int(request.GET['search'])
    except:
        search = None

    
    last_page = (Recipe.objects.all().count()//3)+1
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
    
    recipes = Recipe.objects.order_by('-date')[(page-1)*3:page*3]
    ingredients = Ingredient.objects.all().annotate(count=Count('recipe')).order_by('-count')[:5]
    for recipe in recipes:
        recipe.instructions = recipe.instructions.split('\r\n')
    
    return render(request, 'recipes/index.html',
    {'recipes': recipes, 'ingredients': ingredients, 'page': page,
    'page_range': page_range, 'prev_page': prev_page, 'next_page': next_page,
    'last_page': last_page})