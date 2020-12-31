from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django_extensions.db.fields import AutoSlugField
from martor.models import MartorField


class Ingredient(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False)
    slug = AutoSlugField(populate_from='name', overwrite=True)

    def __str__(self):
        return self.name

    def use_count(self):
        return Ingredient.objects.filter(name=self.name).annotate(count=Count('recipe')).first().count


class Recipe(models.Model):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='%Y/%m/')
    instructions = MartorField()
    difficulty_choices = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]
    difficulty = models.CharField(max_length=10, choices=difficulty_choices, default=EASY)
    ingredients = models.ManyToManyField(Ingredient)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
