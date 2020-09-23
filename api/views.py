from rest_framework.viewsets import ModelViewSet
from .models import Review, Title, Genre, Category
from .serializers import (
    ReviewSerializer, CommentSerializer,
    TitlesSerializer, GenreSerializer, CategorySerializer
)
from django.shortcuts import get_object_or_404
from .pagination import NumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter


class ReviewViewSet(ModelViewSet):
    """Create, get, update reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = []

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
    pagination_class = NumberPagination
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
