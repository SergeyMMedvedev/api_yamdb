from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Review, Comment
from .models import User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        default=None,
    )

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
    )

    class Meta:
        fields = (
                  'first_name',
                  'last_name',
                  'username',
                  'bio',
                  'email',
                  'role',
                  )
        model = User


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=250)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token = token.access_token

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
