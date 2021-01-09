from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('recipe/create/', views.CreateRecipe.as_view(), name='create_recipe'),
    path('recipe/<int:pk>/', views.RecipeDetail.as_view(), name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.EditRecipe.as_view(), name='edit_recipe'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
