from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('create_recipe', views.create_recipe.as_view(), name='create_recipe'),
    path('edit_recipe/<int:pk>', views.edit_recipe.as_view(), name='edit_recipe'),
    path('recipe/<int:pk>', views.recipe_detail.as_view(), name='recipe_detail'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
