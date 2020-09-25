from rest_framework import serializers
from .models import Review, Comment, Title, Genre, Category
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


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

class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitlesSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)

    category = CategorySerializer(read_only=True, many=False)
    rating = serializers.IntegerField(default=None)
    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title


# class TitlesRatingSerializer(serializers.Serializer):
#     id = serializers.Field()
#     name = serializers.CharField()
#     year = serializers.IntegerField()
#
#     genre = GenreSerializer(many=True, read_only=True)
#     rating = serializers.CharField(default=0)
#
#     class Meta:
#         fields = ('id', 'name', 'year', 'category', 'genre', 'rating')









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
