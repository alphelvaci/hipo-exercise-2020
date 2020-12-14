from django import forms
from .models import Recipe


class SearchForm(forms.Form):
    search_keyword = forms.CharField(max_length=50)


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('title', 'image', 'instructions', 'difficulty', 'ingredients')
