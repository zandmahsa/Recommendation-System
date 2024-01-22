from django.core.management.base import BaseCommand
from recommender.models import Movie, Tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import joblib

class Command(BaseCommand):
    help = 'Train and save the TF-IDF model for movie descriptions'

    def handle(self, *args, **options):
        # Retrieve all movies and their associated tags
        all_movies = Movie.objects.all().prefetch_related('tags')
        # Combine movie genres and tags into a single string for each movie
        movie_descriptions = [' '.join([movie.genres] + [tag.tag for tag in movie.tags.all()]) for movie in all_movies]

        # Train the TF-IDF Vectorizer
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(movie_descriptions)
        
        # Calculate cosine similarity matrix
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        # Save the TF-IDF Vectorizer
        joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')

        joblib.dump(cosine_similarities, 'cosine_similarities.joblib')
        
        self.stdout.write(self.style.SUCCESS('Successfully trained and saved the TF-IDF model'))
