import csv
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from recommender.models import Link, Movie, Rating, Tag
from django.utils.dateparse import parse_datetime
from django.db import transaction
import datetime
import pytz
from django.utils.timezone import make_aware
from django.contrib.auth.models import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load data from CSV files into the database'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        logger.info("Starting data import...")
        self.import_movies()
        self.import_links()
        self.import_ratings()
        self.import_tags()
        logger.info('Data import completed successfully')

    def import_movies(self):
        movies_csv_path = settings.BASE_DIR / 'data/movies.csv'
        movie_objects = []

        try:
            with open(movies_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    movie, created = Movie.objects.get_or_create(
                        movie_id=int(row['movieId']),
                        defaults={'title': row['title'], 'genres': row['genres']}
                    )
                    if created:
                        movie_objects.append(movie)

            Movie.objects.bulk_create(movie_objects, ignore_conflicts=True)
            logger.info("Movies imported successfully.")
        except Exception as e:
            logger.error(f"Error while importing movies: {e}")

    def import_links(self):
        links_csv_path = settings.BASE_DIR / 'data/links.csv'
        link_objects = []
        movies = {movie.movie_id: movie for movie in Movie.objects.all()}

        try:
            with open(links_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    movie_id = int(row['movieId'])
                    if movie_id in movies:
                        movie = movies[movie_id]

                        tmdb_id = row['tmdbId']
                        tmdb_id = int(tmdb_id) if tmdb_id.isdigit() else None

                        link, created = Link.objects.get_or_create(
                            movie=movie,
                            defaults={'imdb_id': row['imdbId'], 'tmdb_id': tmdb_id}
                        )
                        if created:
                            link_objects.append(link)
                    else:
                        logger.warning(f"Skipping link for non-existent movie with id {movie_id}.")

            Link.objects.bulk_create(link_objects, ignore_conflicts=True)
            logger.info("Links imported successfully.")
        except Exception as e:
            logger.error(f"Error while importing links: {e}")

    def import_ratings(self):
        ratings_csv_path = settings.BASE_DIR / 'data/ratings.csv'
        rating_objects = []
        user_ids = set()

        try:
            with open(ratings_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    user_id = int(row['userId'])
                    user_ids.add(user_id)
                    movie_id = int(row['movieId'])
                    if Movie.objects.filter(movie_id=movie_id).exists():
                        rating_objects.append(Rating(
                            user_id=user_id,
                            movie_id=movie_id,
                            rating=float(row['rating']),
                            timestamp=parse_datetime(row['timestamp'])
                        ))
                    else:
                        logger.warning(f"Movie with id {movie_id} does not exist, rating skipped.")

            # Create User objects for new users
            for user_id in user_ids:
                User.objects.get_or_create(username=str(user_id))

            Rating.objects.bulk_create(rating_objects, ignore_conflicts=True)
            logger.info("Ratings imported successfully.")
        except Exception as e:
            logger.error(f"Error while importing ratings: {e}")



    def import_tags(self):
        logger.info("Starting to import tags...")
        tags_csv_path = settings.BASE_DIR / 'data/tags.csv'
        tag_objects = []

        with open(tags_csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                movie_id = int(row['movieId'])
                if Movie.objects.filter(movie_id=movie_id).exists():
                    movie = Movie.objects.get(movie_id=movie_id)
                    # Convert epoch time to datetime
                    timestamp = make_aware(datetime.datetime.fromtimestamp(int(row['timestamp'])), pytz.utc)
                    tag_objects.append(Tag(
                        movie=movie,
                        user_id=int(row['userId']),
                        tag=row['tag'],
                        timestamp=timestamp
                    ))
                else:
                    logger.warning(f"Skipping tag for movie ID {movie_id} due to missing or invalid timestamp.")

        try:
            with transaction.atomic():
                Tag.objects.bulk_create(tag_objects)
                logger.info(f"{len(tag_objects)} tags imported successfully.")
        except Exception as e:
            logger.error(f"Failed to import tags due to error: {e}")

