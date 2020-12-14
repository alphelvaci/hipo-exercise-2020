from django import forms


class SearchForm(forms.Form):
    search_keyword = forms.CharField(max_length=50)

