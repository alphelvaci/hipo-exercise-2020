from django.shortcuts import redirect, get_object_or_404
from .models import Ingredient, Recipe
from django.db.models import Count
from .forms import RecipeForm, SearchForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.views.generic import ArchiveIndexView, DetailView, CreateView, UpdateView


class index(ArchiveIndexView):
    date_field = 'date'
    paginate_by = 3
    context_object_name = 'recipes'
    template_name = 'recipes/index.html'

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

    def get_queryset(self):
        queryset = Recipe.objects.order_by('-date')
        if 'ingredient' in self.request.GET:  # filter
            filter_ingredient = self.request.GET['ingredient']
            queryset = Recipe.objects.filter(ingredients__slug=filter_ingredient).order_by('-date')
        elif 'search_keyword' in self.request.GET:  # search
            search_keyword = self.request.GET['search_keyword']
            queryset = self.recipe_search(queryset, search_keyword)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'ingredient' in self.request.GET:
            context['filter_ingredient'] = get_object_or_404(Ingredient, slug=self.request.GET['ingredient'])
        elif 'search_keyword' in self.request.GET:
            context['search_keyword'] = self.request.GET['search_keyword']
        context['user'] = self.request.user
        context['search_form'] = SearchForm
        context['ingredients'] = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
        context['footer_page_range'] = set(context['paginator'].page_range) & set(range(context['page_obj'].number-2, context['page_obj'].number+3))
        return context

    def post(self, request):  # when search form is submitted
        return redirect('/?search_keyword=' + request.POST['search_keyword'])


class recipe_detail(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm
        context['ingredients'] = Ingredient.objects.annotate(count=Count('recipe')).order_by('-count')[:5]
        return context

    def post(self, request):
        return redirect('/?search_keyword=' + request.POST['search_keyword'])


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class create_recipe(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/post_recipe.html'

    def form_valid(self, form):
        recipe = form.save(commit=False)
        recipe.author = self.request.user
        recipe.date = timezone.now()
        recipe.save()
        form.save_m2m()  # create ingredient relations
        return redirect('/recipe/' + str(recipe.id))


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class edit_recipe(UpdateView):
    form_class = RecipeForm
    template_name = 'recipes/post_recipe.html'
    success_url = 'recipes/'

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if get_object_or_404(queryset, pk=self.kwargs['pk']).author == self.request.user:
            return queryset
        else:
            raise Http404

    def form_valid(self, form):
        recipe = form.save()
        return redirect('/recipe/' + str(recipe.id))
