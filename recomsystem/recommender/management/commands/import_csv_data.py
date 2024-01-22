import csv
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from recommender.models import Link, Movie, Rating, Tag
from django.utils.dateparse import parse_datetime
from django.db import transaction



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

        try:
            with open(ratings_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    movie_id = int(row['movieId'])
                    if Movie.objects.filter(movie_id=movie_id).exists():
                        rating_objects.append(Rating(
                            user_id=int(row['userId']),
                            movie_id=movie_id,
                            rating=float(row['rating']),
                            timestamp=parse_datetime(row['timestamp'])
                        ))
                    else:
                        logger.warning(f"Movie with id {movie_id} does not exist, rating skipped.")

            Rating.objects.bulk_create(rating_objects, ignore_conflicts=True)
            logger.info("Ratings imported successfully.")
        except Exception as e:
            logger.error(f"Error while importing ratings: {e}")

    def import_tags(self):
        logger.info("Starting to import tags...")
        tags_csv_path = settings.BASE_DIR / 'data/tags.csv'
        tag_objects = []

        try:
            with open(tags_csv_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    movie_id = int(row['movieId'])
                    if Movie.objects.filter(movie_id=movie_id).exists():
                        movie = Movie.objects.get(movie_id=movie_id)
                        tag_objects.append(Tag(
                            movie=movie,
                            user_id=int(row['userId']),
                            tag=row['tag'],
                            timestamp=parse_datetime(row['timestamp'])
                        ))
                        logger.info(f"Successfully prepared tag for import for movie ID {row['movieId']}")
            Tag.objects.bulk_create(tag_objects, ignore_conflicts=False)
            
            logger.info("Tags imported successfully.")
            #pass
        except Exception as e:
            logger.error(f"Failed to import tags: {e}")
            
        #logger.info("Finished importing tags.")
