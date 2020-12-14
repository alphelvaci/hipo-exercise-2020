from django.shortcuts import render, redirect
from .models import Ingredient, Recipe
from django.db.models import Count
from .forms import RecipeForm, SearchForm


def index(request):
    if request.method == "POST":
        return redirect('/?search_keyword=' + request.POST['search_keyword'])

    # get the html GET parameters
    if 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1
    if 'ingredient' in request.GET:
        filter_ingredient = request.GET['ingredient']
        filtered = True
    else:
        filter_ingredient = None
        filtered = False
    if 'search_keyword' in request.GET:
        search_keyword = request.GET['search_keyword']
        searched = True
    else:
        search_keyword = None
        searched = False

    if filtered:
        recipes = Recipe.objects.filter(ingredients__name=filter_ingredient).order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.filter(ingredients__name=filter_ingredient).count()
    elif searched:
        author_matches = Recipe.objects.filter(author__username__unaccent__icontains=search_keyword)
        title_matches = Recipe.objects.filter(title__unaccent__icontains=search_keyword)
        instruction_matches = Recipe.objects.filter(instructions__unaccent__icontains=search_keyword)
        difficulty_matches = Recipe.objects.filter(difficulty__unaccent__icontains=search_keyword)
        ingredient_matches = Recipe.objects.filter(ingredients__name__unaccent__icontains=search_keyword)
        recipes = (author_matches | title_matches | instruction_matches | difficulty_matches | ingredient_matches).distinct()[(page-1)*3:page*3]
        recipe_count = (author_matches | title_matches | instruction_matches | difficulty_matches | ingredient_matches).distinct().count()
    else:
        recipes = Recipe.objects.order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.count()
    ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
    for recipe in recipes:
        recipe.instructions = recipe.instructions.split('\r\n')

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
        range_start = page + 5
    if page + 5 > last_page:
        range_end = last_page + 1
    else:
        range_end = page - 3
    page_range = range(range_start, range_end)

    return render(
        request, 'recipes/index.html',
        {
            'recipes': recipes,
            'ingredients': ingredients,
            'page': page,
            'page_range': page_range,
            'prev_page': prev_page,
            'next_page': next_page,
            'last_page': last_page,
            'filter_ingredient': filter_ingredient,
            'search_form': SearchForm,
            'search_keyword': search_keyword,
        }
    )
