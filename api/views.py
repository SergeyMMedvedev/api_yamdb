from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSetMixin
from rest_framework.pagination import PageNumberPagination

from .pagination import NumberPagination
from .filters import TitleFilter
from .models import Review, User, Title, Genre, Category
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    TitlesSerializer,
    GenreSerializer,
    UserSerializer,
    TokenSerializer,
    MyTokenObtainPairSerializer,
    CategorySerializer,
    # TitlesRatingSerializer,
)
from .permissions import IsNotAuth, IsAdmin, HasDetailPermission, IsAdminOrReadOnly
from .api_tokens import TokenGenerator
import copy
from django.db.models import Sum



account_activation_token = TokenGenerator()


class ReviewViewSet(ModelViewSet):
    """Create, get, update reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasDetailPermission]
    permission_classes = []
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)


class CommentViewSet(ModelViewSet):
    """Create, get, update comments for reviews"""
    serializer_class = CommentSerializer
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['reviews_id'])
        return review.comments.all()


class TitlesViewSet(ModelViewSet):

    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        for obj in queryset:
            rating = obj.reviews.aggregate(Sum('score')).get('score__sum')
            obj.rating = rating
            obj.save()
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (

            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

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
        if slug_genre or slug_category:
            if slug_genre and slug_category:
                genre = Genre.objects.filter(slug__in=slug_genre)

                category = get_object_or_404(Category, slug=slug_category)
                serializer.save(genre=genre, category=category)
            elif slug_genre:
                genre = Genre.objects.filter(slug__in=slug_genre)
                serializer.save(genre=genre)
            elif slug_category:
                category = get_object_or_404(Category, slug=slug_category)
                serializer.save(category=category)
        else:

            serializer.save()


















class GenreAPI(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny, )


class GenreDestroyAPI(generics.DestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny, )

    def get_object(self):
        obj = self.queryset.get(slug=self.kwargs['slug'])
        return obj


class CategoryAPI(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny, )


class CategoryDestroyAPI(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        obj = self.queryset.get(slug=self.kwargs['slug'])
        return obj





























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
                confirmation_code = account_activation_token.make_token(user)
                mail_subject = 'Activate your account.'
                message = (f"Hello, your confirmation_code: "
                           f"{confirmation_code}")
                to_email = str(request.data.get('email'))
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

                return Response({"email": serializer.data['email']},
                                status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)


class ActivateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = User.objects.get(email=request.data.get('email'))
        if account_activation_token.check_token(user,
                                                request.data.get(
                                                    "confirmation_code")):
            user.is_active = True
            user.set_password("serg112345")
            user.save()
            data = {
                "token": str(MyTokenObtainPairSerializer.get_token(user))
            }
            serializer = TokenSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserAPIListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, permissions.IsAuthenticated)
    pagination_class = PageNumberPagination


class UserAPIRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, permissions.IsAuthenticated)

    def get_object(self):
        user = get_object_or_404(self.queryset,
                                 username=self.kwargs.get('username'))
        return user


class MeAPIRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        user = self.request.user
        return user
