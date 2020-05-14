from django.db import models
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Actor
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewCreateSerializer,
    CreateRatingSerializer,
    ActorListSerialize,
    ActorDetailSerialize
)
from .service import get_client_ip


class ActorsListView(generics.ListAPIView):
    """Вывод Списка актеров"""

    queryset = Actor.objects.all()
    serializer_class = ActorListSerialize


class ActorsDetailView(generics.RetrieveAPIView):
    """Вывод Списка актеров"""

    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerialize


class MovieListView(generics.ListAPIView):
    """Вывод списков фильмов"""
    serializer_class = MovieListSerializer

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count('ratings', filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies


class MovieDetailView(generics.RetrieveAPIView):
    """Вывод фильма"""

    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


class ReviewCreateView(generics.CreateAPIView):
    """Добавление отзыва к фильму"""

    serializer_class = ReviewCreateSerializer


class AddStarRatingView(generics.CreateAPIView):
    """Добавление рейтинга фильму"""

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))