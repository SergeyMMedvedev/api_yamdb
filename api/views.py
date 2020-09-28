from datetime import datetime as dt
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, generics
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .pagination import NumberPagination
from .filters import TitleFilter
from .models import Review, Title, Genre, Category
from .serializers import (
    ReviewSerializer, CommentSerializer, TitlesSerializer, GenreSerializer,
    CategorySerializer, UserSerializer, TokenSerializer,
    ConformationCodeSerializer,
)
from .permissions import (
    IsNotAuth, IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly, UsersPermission
)
from .conformation_code import ConformationCodeGenerator
from django.db.models import Avg

conformation_code_generator = ConformationCodeGenerator()
User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """Create, get, update reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly]

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.check_only_one_review(request):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def check_only_one_review(self, request):
        title_id = int(self.kwargs['title_id'])
        reviews_title_ids = []
        for review in request.user.reviews.all():
            reviews_title_ids.append(review.title.id)

        return title_id not in reviews_title_ids

    def get_queryset(self):
        queryset = get_object_or_404(
            Title, pk=self.kwargs['title_id']
        ).reviews.all()

        return queryset


class CommentViewSet(ModelViewSet):
    """Create, get, update comments for reviews"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review_id=self.kwargs['review_id'],
            pub_date=dt.now()
        )

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return review.comments.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.check_exist()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def check_exist(self):
        get_object_or_404(Review, id=self.kwargs['review_id'])


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def score(self, obj):
        """Movie rating calc"""
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        obj.rating = rating
        obj.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        for obj in queryset:
            self.score(obj)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        slug_genre = self.request.data.get('genre')
        if isinstance(slug_genre, str):
            slug_genre = self.request.data.getlist('genre')
        slug_category = self.request.data.get('category')
        genre = Genre.objects.filter(slug__in=slug_genre)
        category = get_object_or_404(Category, slug=slug_category)
        serializer.save(genre=genre, category=category)

    def perform_update(self, serializer):
        slug_genre = self.request.data.get('genre')
        slug_category = self.request.data.get('category')
        if slug_genre and slug_category:
            genre = Genre.objects.filter(slug__in=slug_genre)
            category = get_object_or_404(Category, slug=slug_category)
            serializer.save(genre=genre, category=category)
        elif slug_genre:
            genre = get_list_or_404(Genre, slug__in=slug_genre)
            serializer.save(genre=genre)
        elif slug_category:
            category = get_object_or_404(Category, slug=slug_category)
            serializer.save(category=category)
        else:
            serializer.save()

    def get_object(self):

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.score(obj)

        """May raise a permission denied"""
        self.check_object_permissions(self.request, obj)

        return obj


class GenreAPIView(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = NumberPagination
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class CategoryAPIView(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = NumberPagination
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class SignupAPIView(APIView):
    permission_classes = [IsNotAuth]
    serializers = UserSerializer

    def post(self, request):
        if not request.user.is_authenticated:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                user = User.objects.create(email=request.data.get('email'))
                user.is_active = False
                user.set_unusable_password()
                user.save()
                confirmation_code = conformation_code_generator.make_token(
                    user)
                mail_subject = 'Activate your account.'
                message = (f"Hello, your confirmation_code: "
                           f"{confirmation_code}")
                to_email = str(request.data.get('email'))
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

                return Response({'email': serializer.data['email']},
                                status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)


class ActivateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = User.objects.get(email=request.data.get('email'))
        if conformation_code_generator.check_token(user,
                                                   request.data.get(
                                                    'confirmation_code')):
            user.is_active = True
            user.save()
            data = {
                'token': str(ConformationCodeSerializer.get_token(user))
            }
            serializer = TokenSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSetMixin,
                  generics.ListCreateAPIView,
                  generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UsersPermission]
    pagination_class = PageNumberPagination

    def get_object(self):
        if self.kwargs.get('username') == 'me':
            user = self.request.user
        else:
            user = get_object_or_404(
                self.queryset, username=self.kwargs.get('username')
            )
        return user

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        if request.data.get('password'):
            request.user.set_password(request.data.get('password'))
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.path.endswith('users/me/'):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
