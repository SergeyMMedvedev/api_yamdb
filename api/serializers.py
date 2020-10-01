from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Review, Comment, Title, Genre, Category

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class RoundingDecimalField(serializers.DecimalField):
    def validate_precision(self, value):
        return value


class TitlesSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True, many=False)
    rating = RoundingDecimalField(
        max_digits=21, decimal_places=2, coerce_to_string=False, default=0,
        read_only=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    title = TitlesSerializer(read_only=True)
    score = serializers.IntegerField(max_value=10)

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            title_id = self.context.get('title').id
            reviews = self.context.get('request').user.reviews.all()
            reviews_id_of_current_author = []
            for review in reviews:
                reviews_id_of_current_author.append(review.title.id)
            if title_id in reviews_id_of_current_author:
                raise serializers.ValidationError('Only one review allowed')
        return attrs

    class Meta:
        fields = '__all__'
        model = Review


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        default=None,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
    )

    class Meta:
        fields = ('first_name', 'last_name',
                  'username', 'bio', 'email', 'role',)
        model = User


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=250)


class ConfirmationCodeSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token = token.access_token

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = ConfirmationCodeSerializer
