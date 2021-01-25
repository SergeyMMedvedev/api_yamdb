from datetime import datetime as dt
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, generics
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .pagination import NumberPagination
from .filters import TitleFilter
from .models import Review, Title, Genre, Category
from .serializers import (
    ReviewSerializer, CommentSerializer, TitlesSerializer, GenreSerializer,
    CategorySerializer, UserSerializer, TokenSerializer,
    ConfirmationCodeSerializer,
)
from .permissions import (
    IsNotAuth, IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly,
    IsAdmin,
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated
)
from .confirmation_code import ConfirmationCodeGenerator
from django.db.models import Avg

confirmation_code_generator = ConfirmationCodeGenerator()
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

    def get_queryset(self):
        queryset = get_object_or_404(
            Title, pk=self.kwargs['title_id']
        ).reviews.all()
        return queryset

    def get_serializer_context(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        context = super(ReviewViewSet, self).get_serializer_context()
        context.update({"request": self.request, 'title': title})
        return context


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


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitlesSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

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


@api_view(http_method_names=['POST'])
@permission_classes((IsNotAuth, ))
def send_email(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create(email=request.data.get('email'))
        user.is_active = False
        user.set_unusable_password()
        user.save()
        confirmation_code = confirmation_code_generator.make_token(
            user)
        mail_subject = 'Activate your account.'
        message = (f"Hello, your confirmation_code: "
                   f"{confirmation_code}")
        to_email = str(request.data.get('email'))
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return Response({'email': serializer.data['email'],
                         'confirmation code': str(confirmation_code)},
                                status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])
@permission_classes((AllowAny, ))
def send_JWT(request):
    user = User.objects.get(email=request.data.get('email'))
    if confirmation_code_generator.check_token(user,
                                               request.data.get(
                                               'confirmation_code')):
        user.is_active = True
        user.save()
        data = {
            'token': str(ConfirmationCodeSerializer.get_token(user))
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
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination

    def get_object(self):
        user = get_object_or_404(
            self.queryset, username=self.kwargs.get('username')
        )
        return user

    @action(methods=['GET', 'PATCH', 'DELETE'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == 'PATCH':
            if request.data.get('password'):
                request.user.set_password(request.data.get('password'))
            kwargs['partial'] = True
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(user, data=request.data,
                                             partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        if request.method == 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
