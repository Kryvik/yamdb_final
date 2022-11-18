from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Comment, Review, User
from titles.models import Category, Genre, Title

from .confirmation_code import get_random_code
from .custom_viewset import AuthViewSet, GetPostDelViewSet
from .filter import TitlesFilter
from .permissions import (IsAdminOrReadOnly, IsAdminRoleOrGetListOnly,
                          IsAuthOrReadOnly, OnlyAdminOrMe)
from .serializers import (AuthSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, MeSerializer,
                          ReviewSerializer, TitlesCreateSerializer,
                          TitlesSerializer, UserSerializer)
from .utils import Round


class AuthSignUpViewSet(AuthViewSet):
    queryset = User.objects.all()
    serializer_class = AuthSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            instance = User.objects.get(username=username)
            confirmation_code = instance.confirmation_code
            serializer = self.get_serializer(instance)
        else:
            confirmation_code = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        send_mail(
            'Код подтверждения',
            confirmation_code,
            settings.ADMIN_EMAIL,
            [self.request.data['email']],
            fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer):
        confirmation_code = get_random_code()
        serializer.save(confirmation_code=confirmation_code)
        return confirmation_code


class UserGetTokenView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        refresh = RefreshToken.for_user(user)
        serializer.validated_data['token'] = str(refresh.access_token)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (OnlyAdminOrMe,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save(confirmation_code=get_random_code())

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='me')
    def information_about_me(self, request):
        user = self.request.user
        if self.request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if self.request.method == 'PATCH':
            partial = self.kwargs.pop('partial', False)
            serializer = MeSerializer(user, data=request.data,
                                      partial=partial, context=user)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)


class GenreViewSet(GetPostDelViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminRoleOrGetListOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class CategoryViewSet(GetPostDelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminRoleOrGetListOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Round(Avg('reviews__score'))).order_by('id')
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitlesCreateSerializer
        return TitlesSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset для ревью."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthOrReadOnly,)

    def get_queryset(self):
        pk = self.kwargs.get('title_id')
        get_object_or_404(Title, pk=pk)
        return Review.objects.filter(title__pk=pk)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthOrReadOnly,)

    def get_queryset(self):
        pk = self.kwargs.get('review_id')
        get_object_or_404(Review, pk=pk)
        return Comment.objects.filter(review__pk=pk)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
