import datetime

from rest_framework import serializers
from titles.models import Category, Comment, Genre, Review, Title
from users.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all())
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, year):
        """
        Проверка поля 'year'
        """
        current_year = datetime.date.today().year
        if year > current_year:
            raise serializers.ValidationError(
                'Год произведения не может быть больше текущего'
            )
        return year


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        """
        Разрешить пользователям оставлять только один отзыв на произведение.
        """
        request = self.context.get('request')
        if request.method != 'POST':
            return data

        title_id = self.context.get('view').kwargs.get('title_id')
        user = self.context.get('request').user
        queryset = Review.objects.filter(author=user, title=title_id)
        if queryset.exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'username', 'role', 'email', 'bio'
        )

    def validate_email(self, value):
        """
        email должен быть уникальным.
        """
        request = self.context.get('request')
        if request.method != 'POST':
            return value
        queryset = CustomUser.objects.filter(email=value)
        if queryset.exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует!'
            )
        return value

    def validate_username(self, value):
        """
        username должны быть уникальным.
        """
        request = self.context.get('request')
        if request.method != 'POST':
            return value
        queryset_username = CustomUser.objects.filter(
            username=value
        )
        if queryset_username.exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует!'
            )
        return value


class UserRoleReadOnlySerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class EmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ('email',)


class EmailCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = ('email', 'code')
