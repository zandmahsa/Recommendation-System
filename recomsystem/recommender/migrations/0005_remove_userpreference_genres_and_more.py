# Generated by Django 5.0.1 on 2024-01-09 18:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recommender", "0004_genre_userpreference"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userpreference",
            name="genres",
        ),
        migrations.RemoveField(
            model_name="userpreference",
            name="user",
        ),
        migrations.CreateModel(
            name="GenrePreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("genres", models.CharField(max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Genre",
        ),
        migrations.DeleteModel(
            name="UserPreference",
        ),
    ]
