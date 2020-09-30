from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ReviewViewSet, CommentViewSet,
    TitleViewSet, GenreAPIView, CategoryAPIView,
    UserViewSet,
    send_email,
    send_JWT
)
from django.urls import path, include


router = DefaultRouter()
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>[0-9]+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>[0-9]+)/reviews/'
                r'(?P<review_id>[0-9]+)/comments',
                CommentViewSet, basename='comments'),
router.register(r'genres', GenreAPIView, basename='genres')
router.register(r'categories', CategoryAPIView, basename='categories')
router.register(r'users', UserViewSet, basename='users',)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('v1/auth/email/', send_email),
    path('v1/auth/token/', send_JWT),
]
