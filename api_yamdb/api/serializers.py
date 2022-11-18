from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Comment, Review, User
from titles.models import Category, Genre, Title
from users.models import CHOICES_ROLE


class AuthSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        value = value.lower()
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.')
        return value


class UserGetTokenSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField()

    def validate(self, data):
        username = data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = data['confirmation_code']
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                'Не валидный код подтверждения'
            )
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class MeSerializer(serializers.ModelSerializer):
    username = serializers.PrimaryKeyRelatedField(read_only=True)
    email = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User

    def validate(self, data):
        user = self.context
        role = data.get('role')
        if user.role == CHOICES_ROLE[0][0] and (role is not None
                                                or role != CHOICES_ROLE[0][0]):
            data['role'] = 'user'
        return data


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitlesSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField(max_value=10, min_value=1)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title


class TitlesCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )
        model = Title

    def validate_year(self, value):
        current_year = timezone.now().year
        if not value <= current_year:
            raise serializers.ValidationError('Проверьте год создания.')
        return value


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get('view').kwargs.get('title_id')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""
    author = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=CurrentTitleDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
