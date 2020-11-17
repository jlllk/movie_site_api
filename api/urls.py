from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    AuthInfoEmailAPIView,
    AuthInfoTokenAPIView,
    CategoriesViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet
)

v1_router = DefaultRouter()

v1_router.register('categories', CategoriesViewSet, 'categories')
v1_router.register('titles', TitleViewSet, 'titles'),
v1_router.register('genres', GenreViewSet),
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    'comments'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    'reviews'
)

urlpatterns = []

v1_auth = [
    path('email/', AuthInfoEmailAPIView.as_view()),
    path('token/', AuthInfoTokenAPIView.as_view()),
]

v1_urlpatterns = [
    path('v1/auth/', include(v1_auth)),
    path('v1/', include(v1_router.urls)),
]


urlpatterns += v1_urlpatterns
