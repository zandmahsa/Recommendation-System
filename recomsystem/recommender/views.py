from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Movie, Link, Tag, Rating, GenrePreference, Recommendation
from .forms import RatingForm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib import messages
from sklearn.metrics.pairwise import linear_kernel
import joblib
from .forms import GenrePreferenceForm
from django.http import HttpResponseForbidden



def home(request):
    genre_form = None

    if request.user.is_authenticated:
        try:
            genre_pref_instance = GenrePreference.objects.get(user=request.user)
            initial_genres = genre_pref_instance.genres.split(',')  

        except GenrePreference.DoesNotExist:
            genre_pref_instance = None
            initial_genres = []

        if request.method == 'POST':
            genre_form = GenrePreferenceForm(request.POST, instance=genre_pref_instance)
            if genre_form.is_valid():
                selected_genres = ','.join(genre_form.cleaned_data['genres'])
                if genre_pref_instance:
                    genre_pref_instance.genres = selected_genres
                    genre_pref_instance.save()
                else:
                    GenrePreference.objects.create(user=request.user, genres=selected_genres)
                
                messages.success(request, 'Your genre preferences were submitted successfully.')

                return redirect('home')
        else:
            initial_genres = genre_pref_instance.genres.split(',') if genre_pref_instance else []
            genre_form = GenrePreferenceForm(initial={'genres': initial_genres})
    else:
        genre_form = None

    return render(request, 'recommender/home.html', {'genre_form': genre_form})


def custom_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = UserCreationForm()
    return render(request, 'recommender/register.html', {'form': form})


@login_required
def profile(request):
    if Rating.objects.filter(user_id=request.user.id).count() < 5:
        recommended_movies = recommend_movies_for_new_users(request.user.id)

    else:
        recommended_movies = recommend_movies_content_based(request.user.id)

    # fetch preference-based recommended movies
    preference_recommended_movies = recommend_movies_based_on_preferences(request.user.id)

    #fetch additional content-based recommendations
    additional_recommendations = recommend_movies_content_based(request.user.id)  

    #fetch a general list of popular movies
    movie_list = Movie.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:10]
    
   
    movies_per_page = 6
    paginator = Paginator(preference_recommended_movies, movies_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'recommender/profile.html', {
        'recommended_movies': recommended_movies,
        'additional_recommendations': additional_recommendations,  
        'movie_list': movie_list,
        'preference_recommended_movies': preference_recommended_movies,
        'page_obj': page_obj,
    })


@login_required
def movie_list(request):
    movies = Movie.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
    
    # get user ratings
    user_ratings = Rating.objects.filter(user_id=request.user.id).values('movie_id', 'rating')
    user_ratings_dict = {rating['movie_id']: rating['rating'] for rating in user_ratings}

    
    movies_with_ratings = []
    for movie in movies:
        movies_with_ratings.append({
            'movie': movie,
            'user_rating': user_ratings_dict.get(movie.id)
        })

    paginator = Paginator(movies_with_ratings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'recommender/movie_list.html', {'page_obj': page_obj})



@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    links = Link.objects.filter(movie=movie)

    #tags = Tag.objects.filter(movie=movie)
    tag_values = Tag.objects.filter(movie=movie).values_list('tag', flat=True).distinct()
    unique_tags = set(tag_values)


    form = RatingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        Rating.objects.update_or_create(
            user_id=request.user.id,
            movie=movie,
            defaults={'rating': form.cleaned_data['rating']}
        )
        messages.success(request, 'Your rate was submitted successfully.')
    return render(request, 'recommender/movie_detail.html', {
        'movie': movie,
        'links': links,
        'tags': unique_tags,
        'form': form  
    })

def concatenate_tags(movie_id):
    tags = Tag.objects.filter(movie_id=movie_id).values_list('tag', flat=True)
    return ' '.join(tags)



def get_tfidf_vectorizer():
    return joblib.load('tfidf_vectorizer.joblib')


def recommend_movies_content_based(user_id):
    tfidf_vectorizer = get_tfidf_vectorizer()

    user_high_rated_movies = Rating.objects.filter(user_id=user_id, rating__gte=3).values_list('movie_id', flat=True)
    if not user_high_rated_movies:
        return Movie.objects.none()
    movies_with_tags = Movie.objects.filter(id__in=user_high_rated_movies).prefetch_related('tags')

    user_movie_descriptions = {
        movie.id: ' '.join([movie.genres] + [tag.tag for tag in movie.tags.all()])
        for movie in movies_with_tags
    }

    
    user_movie_vectors = tfidf_vectorizer.transform(user_movie_descriptions.values())

    
    all_movies = Movie.objects.all().prefetch_related('tags')
    all_movie_descriptions = {
        movie.id: ' '.join([movie.genres] + [tag.tag for tag in movie.tags.all()])
        for movie in all_movies
    }
    all_movie_vectors = tfidf_vectorizer.transform(all_movie_descriptions.values())

    #cosine similarities between the user's vectors and all movie vectors
    cosine_similarities = linear_kernel(user_movie_vectors, all_movie_vectors)

  
    movie_index_to_id_mapping = list(all_movie_descriptions.keys())

    # get top 5 similar movies for each movie the user has rated highly
    recommendations = {}
    for idx, movie_id in enumerate(user_movie_descriptions.keys()):
        similar_indices = cosine_similarities[idx].argsort()[:-6:-1]  
        similar_movies = [movie_index_to_id_mapping[i] for i in similar_indices if movie_index_to_id_mapping[i] != movie_id][1:]
        recommendations[movie_id] = similar_movies

    flat_recommendations = set([movie_id for sublist in recommendations.values() for movie_id in sublist])

    recommended_movies = Movie.objects.filter(id__in=flat_recommendations)
    return recommended_movies

@login_required
def get_recommended_movies(user_id):
    return recommend_movies_content_based(user_id)


def recommend_movies_for_new_users(user_id):
    user_pref = GenrePreference.objects.filter(user=user_id).first()
    if user_pref:
        preferred_genres = user_pref.genres.split(',')
        recommended_movies = Movie.objects.filter(genres__in=preferred_genres)[:10]
    else:
        recommended_movies = Movie.objects.all()[:10]
    return recommended_movies


def recommend_movies_based_on_preferences(user_id):
    user_pref = GenrePreference.objects.filter(user=user_id).first()
    recommended_movies = []

    if user_pref:
        preferred_genres = user_pref.genres.split(',')
        
        movies_based_on_preferences = Movie.objects.filter(genres__in=preferred_genres)

        high_rated_movie_ids = Rating.objects.filter(user_id=user_id, rating__gte=4).values_list('movie_id', flat=True)
        high_rated_movies = Movie.objects.filter(id__in=high_rated_movie_ids)

        recommended_movies = (movies_based_on_preferences | high_rated_movies).distinct()

    return recommended_movies


@login_required
def user_recommendations(request):
    recommendations = Recommendation.objects.filter(user=request.user)
    return render(request, 'recommendations.html', {'recommendations': recommendations})
