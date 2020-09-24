from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ReviewViewSet,
    CommentViewSet,
    SignupAPIView,
    ActivateAPIView,
    UserAPIListCreate,
    UserAPIRetrieveUpdateDestroy,
    TestAPI,
    MeAPIRetrieveUpdate,
)
from django.urls import path, include


router = DefaultRouter()
router.register(r'titles/(?P<title_id>[0-9]+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>[0-9]+)/reviews/'
                r'(?P<reviews_id>[0-9]+)/comments',
                CommentViewSet, basename='comments')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('v1/auth/email/', SignupAPIView.as_view()),
    path('v1/auth/token/', ActivateAPIView.as_view()),
    path('v1/users/', UserAPIListCreate.as_view()),
    path('v1/users/me/', MeAPIRetrieveUpdate.as_view()),
    path('v1/users/<str:username>/', UserAPIRetrieveUpdateDestroy.as_view()),
    path('v1/test/', TestAPI.as_view()),
]

