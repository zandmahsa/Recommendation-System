from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from recommender import views as recommender_views
from recommender.views import movie_list, movie_detail
from recommender.views import custom_logout



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='recommender/login.html'), name='login'),
    path('register/', recommender_views.register, name='register'),
    path('', recommender_views.home, name='home'),

    path('accounts/profile/', recommender_views.profile, name='profile'),
    
    path('logout/', custom_logout, name='logout'),
    path('movies/', movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', movie_detail, name='movie_detail'),
   # path('set-genre-preferences/', recommender_views.set_genre_preferences, name='set_genre_preferences'),

    

]