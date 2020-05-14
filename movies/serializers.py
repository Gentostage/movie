from rest_framework import serializers

from .models import Movie, Review, Rating, RatingStar, Actor


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзова к фильму"""

    class Meta:
        model = Review
        fields = '__all__'


class FilterReviewListSerializer(serializers.ListSerializer):
    """Вывод только родительских"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.ModelSerializer):
    """Вывод рекирусивно список коментариев"""

    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователем"""

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star', None)}
        )
        return rating


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзова к фильмов"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ('name', 'text', 'children')


class ActorListSerialize(serializers.ModelSerializer):
    """Вывод списка актера и режесеров"""

    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerialize(serializers.ModelSerializer):
    """Вывод актера или режесеров"""

    class Meta:
        model = Actor
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'tagline', 'category', 'rating_user', 'middle_star')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    directors = ActorListSerialize(read_only=True, many=True)
    actors = ActorListSerialize(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft',)
