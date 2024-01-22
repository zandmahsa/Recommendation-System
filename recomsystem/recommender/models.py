from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.contrib.auth.models import User

#from .models import Rating
import numpy as np
from collections import defaultdict


class Movie(models.Model):
    movie_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title

class Link(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='links', null=True)
    #movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='links')
    imdb_id = models.CharField(max_length=15, blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)

class Rating(models.Model):
    user_id = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField()
    #timestamp = models.DateTimeField()
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        
        super(Rating, self).save(*args, **kwargs)  # Save the rating instance

        # Recalculate the average rating for the related movie
        new_avg = Rating.objects.filter(movie=self.movie).aggregate(Avg('rating'))['rating__avg']
        
        # Update the average rating of the movie
        self.movie.average_rating = new_avg if new_avg is not None else 0.0
        self.movie.save()

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'movie']),
            # Additional indexes can be added here
        ]

class Tag(models.Model):
    user_id = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='tags', null=True)
    tag = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'movie']),
            
        ]


class GenrePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genres = models.CharField(max_length=255)  # Store comma-separated genre preferences

    def __str__(self):
        return f"{self.user.username}'s genre preferences"

    






def get_movie_rating_vectors():
    """
    Retrieves all ratings from the database and constructs a dictionary where
    keys are movie_ids and values are lists of tuples (user_id, rating).
    """
    # Fetch all ratings from the database
    ratings = Rating.objects.all().values_list('movie_id', 'user_id', 'rating')

    # Initialize a default dictionary to hold lists of tuples (user_id, rating) for each movie
    movie_rating_vectors = defaultdict(list)

    # Populate the dictionary
    for movie_id, user_id, rating in ratings:
        movie_rating_vectors[movie_id].append((user_id, rating))

    return movie_rating_vectors

def get_user_rating_vectors():
    """
    Retrieves all ratings from the database and constructs a dictionary where
    keys are user_ids and values are lists of tuples (movie_id, rating).
    """
    # Fetch all ratings from the database
    ratings = Rating.objects.all().values_list('user_id', 'movie_id', 'rating')

    # Initialize a default dictionary to hold lists of tuples (movie_id, rating) for each user
    user_rating_vectors = defaultdict(list)

    # Populate the dictionary
    for user_id, movie_id, rating in ratings:
        user_rating_vectors[user_id].append((movie_id, rating))

    return user_rating_vectors
