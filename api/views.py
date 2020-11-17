from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from api_yamdb.settings import (
    CONF_CODE_STRING,
    DEFAULT_FROM_EMAIL,
    SUBJECT_CONFIRMATION
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from titles.filters import TitleFilter
from titles.models import Category, Comment, Genre, Review, Title
from titles.permissions import IsAdmin, IsModerator, IsOwner, ReadOnly
from users.models import CustomUser

from .serializers import (
    CategorySerializer,
    CommentSerializer,
    EmailCodeSerializer,
    EmailSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateSerializer,
    TitleListSerializer,
    UserRoleReadOnlySerializer,
    UserSerializer
)


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoriesViewSet(ListCreateDestroyViewSet):
    """
    На запрос с методом 'GET' возвращаются все категории.
    Только админ может создавать или удалять категории.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (ReadOnly | IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """
    На запрос с методом 'GET' возвращаются все жанры.
    Только админ может создавать или удалять жанры.
    """
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (ReadOnly | IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    На запрос с методом 'GET' возвращаются все произведения.
    Только админ может создавать, изменять или удалять произведения.
    """
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (ReadOnly | IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter

    def get_serializer_class(self):
        """"
        Переопределение serializer в
        зависимости от методов создания/получения объектов.
        """
        if self.action in ('retrieve', 'list'):
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    На запрос с методом 'GET' возвращаются все отзывы на произведение из
    запроса. Только автор, модератор или админ могут изменять или удалять
    отзывы.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (ReadOnly | IsOwner | IsModerator | IsAdmin,)

    def get_queryset(self):
        """
        Возвращаем только те отзывы, которые принадлежат произведению из
        запроса.
        """
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        """
        Метод создает новый отзыв. В процессе полю author присваивается
        текущий пользователь, а полю title — произведение из запроса.
        """
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    """
    На запрос с методом 'GET' возвращаются все комментарии к отзыву из запроса.
    Только автор, модератор или админ могут изменять или удалять комментарии.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (ReadOnly | IsOwner | IsModerator | IsAdmin,)

    def get_queryset(self):
        """
        Возвращаем только те комментарии, которые принадлежат отзыву из
        запроса.
        """
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title__id=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        """
        Метод создает новый комментарий к отзыву. В процессе полю author
        присваивается текущий пользователь, а полю review — отзыв из запроса.
        """
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review_id=review.id)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(viewsets.ModelViewSet):
    """
    Просматривать, создавать, изменять и удалять профайлы пользователей
    может только администратор.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(detail=False, url_path='me', url_name='user_profile',
            permission_classes=(IsAuthenticated,))
    def user_data(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @user_data.mapping.patch
    def update_user_data(self, request):
        serializer = UserRoleReadOnlySerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AuthInfoEmailAPIView(generics.CreateAPIView):
    """
    Получает email, если пользователь с такии email существует, то заново
    высылает confirmation_code, если нет, то создает нового пользователя, где
    username совпадает с email.
    Затем отправляет на этот email confirmation_code
    """

    permission_classes = (AllowAny,)

    def create(self, request):

        email = request.data.get('email')
        serializer = EmailSerializer(data={'email': email})
        serializer.is_valid(raise_exception=True)
        user, created = CustomUser.objects.get_or_create(
            username=email, email=email)
        code = default_token_generator.make_token(user)
        send_mail(
            SUBJECT_CONFIRMATION,
            '{0}: {1}'.format(CONF_CODE_STRING, code),
            DEFAULT_FROM_EMAIL,
            [email],
        )
        return Response({'email': email})


class AuthInfoTokenAPIView(generics.CreateAPIView):
    """
    Получает email и confirmation_code, если эта пара валидна,
    то выдает часть access токена JWT, который действителен 1 сутки
    """
    permission_classes = (AllowAny,)

    def create(self, request):
        email = request.data.get('email')
        code = request.data.get('confirmation_code')
        serializer = EmailCodeSerializer(data={'email': email, 'code': code})
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(CustomUser, email=email)

        if not default_token_generator.check_token(user, code):
            raise ValidationError('Неверный код подтверждения!')

        token = get_tokens_for_user(user).get('access')

        return Response({'token': token})
