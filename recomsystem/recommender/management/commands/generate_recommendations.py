from django.core.management.base import BaseCommand
from recommender.models import Movie, GenrePreference
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity

class Command(BaseCommand):
    help = 'Generate movie recommendations for users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating movie recommendations...'))

        # Load the TF-IDF model
        tfidf_vectorizer = joblib.load('tfidf_vectorizer.joblib')

        
        user_id = 1  # for example
        recommendations = self.generate_recommendations(user_id, tfidf_vectorizer)
        
        for movie in recommendations:
            self.stdout.write(self.style.SUCCESS(f'Recommended Movie: {movie.title}'))

    def generate_recommendations(self, user_id, tfidf_vectorizer):
        # fetch user's genre preferences
        user_pref = GenrePreference.objects.filter(user_id=user_id).first()
        if not user_pref:
            return []

        user_preferences = user_pref.genres

        
        all_movies = Movie.objects.all().prefetch_related('tags')
        movie_descriptions = [' '.join([movie.genres] + [tag.tag for tag in movie.tags.all()]) for movie in all_movies]
        tfidf_matrix = tfidf_vectorizer.transform(movie_descriptions)

        
        user_tfidf = tfidf_vectorizer.transform([user_preferences])

        
        user_similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()

        
        top_movie_indices = user_similarity_scores.argsort()[-5:][::-1]

        
        recommended_movie_ids = [Movie.objects.all().order_by('id')[int(index)].id for index in top_movie_indices]
        recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)

        return recommended_movies
