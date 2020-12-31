from django.contrib import admin
from .models import Recipe, Ingredient
from martor.widgets import AdminMartorWidget
from django.db import models


class RecipeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
