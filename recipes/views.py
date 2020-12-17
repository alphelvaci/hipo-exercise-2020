from django.shortcuts import render, redirect
from .models import Ingredient, Recipe
from django.db.models import Count
from .forms import RecipeForm, SearchForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .functions import calculate_page_params


def index(request):
    if request.method == "POST":  # when search form is submitted
        return redirect('/?search_keyword=' + request.POST['search_keyword'])

    # set default values
    page = 1
    filter_ingredient = None
    search_keyword = None

    # get the html GET parameters
    if 'page' in request.GET:
        page = int(request.GET['page'])

    if 'ingredient' in request.GET:  # filter
        filter_ingredient = request.GET['ingredient']
        recipes = Recipe.objects.filter(ingredients__name=filter_ingredient).order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.filter(ingredients__name=filter_ingredient).count()
    elif 'search_keyword' in request.GET:  # search
        search_keyword = request.GET['search_keyword']
        author_matches = Recipe.objects.filter(author__username__unaccent__icontains=search_keyword)
        title_matches = Recipe.objects.filter(title__unaccent__icontains=search_keyword)
        instruction_matches = Recipe.objects.filter(instructions__unaccent__icontains=search_keyword)
        difficulty_matches = Recipe.objects.filter(difficulty__unaccent__icontains=search_keyword)
        ingredient_matches = Recipe.objects.filter(ingredients__name__unaccent__icontains=search_keyword)
        recipes = (author_matches | title_matches | instruction_matches | difficulty_matches | ingredient_matches).distinct().order_by('-date')[(page-1)*3:page*3]
        recipe_count = (author_matches | title_matches | instruction_matches | difficulty_matches | ingredient_matches).distinct().count()
    else:
        recipes = Recipe.objects.order_by('-date')[(page-1)*3:page*3]
        recipe_count = Recipe.objects.count()

    ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]

    for recipe in recipes:  # split instructions into lines
        recipe.instructions = recipe.instructions.split('\r\n')

    # calculate variables used for page navigation
    page_params = calculate_page_params(recipe_count, page)
    prev_page = page_params['prev_page']
    next_page = page_params['next_page']
    last_page = page_params['last_page']
    page_range = page_params['page_range']

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
            'user': request.user,
        }
    )


def recipe_detail(request):
    if request.method == "POST":
        return redirect('/?search_keyword=' + request.POST['search_keyword'])

    if 'recipe' in request.GET:
        recipe_id = int(request.GET['recipe'])
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe.instructions = recipe.instructions.split('\r\n')
        ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
    else:
        return render(request, '404.html')

    return render(
        request, 'recipes/recipe_detail.html',
        {
            'recipe': recipe,
            'ingredients': ingredients,
            'search_form': SearchForm,
        }
    )


@login_required
def post_recipe(request):
    edit_mode = False
    recipe = None
    if request.method == "POST":
        if request.POST['edit_mode'] == 'True':
            recipe_id = int(request.POST['recipe'])
            recipe = Recipe.objects.get(pk=recipe_id)
            form = RecipeForm(request.POST, request.FILES, instance=recipe)
        else:
            form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.date = timezone.now()
            recipe.save()
            form.save_m2m()
            return redirect('/')
    elif 'recipe' in request.GET:
        recipe_id = int(request.GET['recipe'])
        recipe = Recipe.objects.get(pk=recipe_id)
        form = RecipeForm(instance=recipe)
        edit_mode = True
    else:
        form = RecipeForm()
    return render(
        request, 'recipes/post_recipe.html',
        {
            'form': form,
            'edit_mode': edit_mode,
            'recipe': recipe,
        }
    )
