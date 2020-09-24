import json

from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSetMixin
from rest_framework.pagination import PageNumberPagination

from .models import Review, User
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    TokenSerializer,
    MyTokenObtainPairSerializer,
)
from .permissions import IsNotAuth, IsAdmin, HasDetailPermission
from .api_tokens import TokenGenerator


account_activation_token = TokenGenerator()


class ReviewViewSet(ModelViewSet):
    """Create, get, update reviews"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasDetailPermission]
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








### delete!!!


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


class TestAPI(APIView):

    def get(self, request):
        user_model = get_user_model()


        user = self.request.user
        refresh = RefreshToken.for_user(user)
        user = get_user_model().objects.get(username='reviewer')
        data = json.dumps({"test": "test",
                           "user_model": str(user_model),
                           "user reviewer": str(user)
                           })

        return Response(data, status=status.HTTP_200_OK)

