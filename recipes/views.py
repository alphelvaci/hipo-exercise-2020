from django.shortcuts import render, redirect, get_object_or_404
from .models import Ingredient, Recipe
from django.db.models import Count
from .forms import RecipeForm, SearchForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.core.paginator import Paginator
from django.views import View


class index(View):
    def recipe_search(self, recipes, search_keyword):
        # get all the possible matches
        author_matches = recipes.filter(author__username__unaccent__icontains=search_keyword)
        title_matches = recipes.filter(title__unaccent__icontains=search_keyword)
        instruction_matches = recipes.filter(instructions__unaccent__icontains=search_keyword)
        difficulty_matches = recipes.filter(difficulty__unaccent__icontains=search_keyword)
        ingredient_matches = recipes.filter(ingredients__name__unaccent__icontains=search_keyword)
        # combine all the matches with the OR operator. use .distinct() to avoid duplicates
        recipes = (author_matches | title_matches | instruction_matches | difficulty_matches | ingredient_matches
                   ).distinct().order_by('-date')
        return recipes

    def get(self, request):
        # set default values
        current_page = 1
        filter_ingredient = None
        search_keyword = None
        recipes = Recipe.objects.order_by('-date')
        paginated_recipes = Paginator(recipes, 3)

        # get the html GET parameters
        if 'ingredient' in request.GET:  # filter
            filter_ingredient = request.GET['ingredient']
            recipes = recipes.filter(ingredients__name=filter_ingredient)

        elif 'search_keyword' in request.GET:  # search
            search_keyword = request.GET['search_keyword']
            recipes = self.recipe_search(recipes, search_keyword)

        paginated_recipes = Paginator(recipes, 3)

        if 'page' in request.GET:
            page_is_valid = False
            page = request.GET['page']
            try:
                page = int(page)
                if page in paginated_recipes.page_range:
                    page_is_valid = True
            except ValueError:
                pass
            if page_is_valid:
                current_page = page
            else:
                raise Http404()

        recipes = paginated_recipes.page(current_page)

        # calculate variables used for page navigation
        last_page = paginated_recipes.page_range[-1]
        if recipes.has_previous():
            prev_page = recipes.previous_page_number()
        else:
            prev_page = 1
        if recipes.has_next():
            next_page = recipes.next_page_number()
        else:
            next_page = last_page
        page_range = set(paginated_recipes.page_range) & set(range(current_page-3, current_page+3))

        # sidebar ingredients
        ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]

        return render(
            request, 'recipes/index.html',
            {
                'recipes': recipes,
                'ingredients': ingredients,
                'page': current_page,
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

    def post(self, request):  # when search form is submitted
        return redirect('/?search_keyword=' + request.POST['search_keyword'])


class recipe_detail(View):
    def get(self, request):
        recipe_id_valid = False
        if 'recipe' in request.GET:
            try:
                recipe_id = int(request.GET['recipe'])
                recipe_id_valid = True
            except ValueError:
                pass

        if not recipe_id_valid:
            raise Http404()

        recipe = get_object_or_404(Recipe, pk=recipe_id)
        ingredients = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
        return render(
            request, 'recipes/recipe_detail.html',
            {
                'recipe': recipe,
                'ingredients': ingredients,
                'search_form': SearchForm,
            }
        )

    def post(self, request):
        return redirect('/?search_keyword=' + request.POST['search_keyword'])


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class post_recipe(View):
    def get(self, request):
        recipe = None
        edit_mode = False
        authorized = False
        recipe_id_valid = False
        form = RecipeForm()

        if 'recipe' in request.GET:
            try:
                recipe_id = int(request.GET['recipe'])
                recipe_id_valid = True
            except ValueError:
                pass
            if recipe_id_valid:
                recipe = get_object_or_404(Recipe, pk=recipe_id)
                form = RecipeForm(instance=recipe)
                edit_mode = True
                authorized = request.user.username == recipe.author.username
            if not (authorized and recipe_id_valid):
                raise Http404()

        return render(
            request, 'recipes/post_recipe.html',
            {
                'form': form,
                'edit_mode': edit_mode,
                'recipe': recipe,
            }
        )

    def post(self, request):
        authorized = False
        recipe_id_valid = False

        if request.POST['edit_mode'] == 'True':
            # create the form from a recipe instance if editing
            try:
                recipe_id = int(request.POST['recipe'])
                recipe_id_valid = True
            except ValueError:
                pass
            if recipe_id_valid:
                recipe = get_object_or_404(Recipe, pk=recipe_id)
                form = RecipeForm(request.POST, request.FILES, instance=recipe)
                authorized = request.user.username == recipe.author.username
                if form.is_valid() and authorized:
                    recipe = form.save()
            if not (authorized and recipe_id_valid):
                raise Http404()
        else:
            form = RecipeForm(request.POST, request.FILES)
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.author = request.user
                recipe.date = timezone.now()
                recipe.save()
                form.save_m2m()  # create ingredient relations

        return redirect('/recipe_detail?recipe=' + str(recipe.id))
