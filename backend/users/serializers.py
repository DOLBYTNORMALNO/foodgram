import django.contrib.auth.password_validation as validators
from django.core import exceptions
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from recipes.serializers import SubscribeRecipeSerializer
from .models import User, Follow


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj, user=self.context['request'].user
        ).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        author = get_object_or_404(User, id=obj.pk)
        recipes = author.recipes.all()
        limit = request.GET.get('recipes_limit')
        try:
            recipes = recipes[:int(limit)] if limit else recipes
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {'recipes_limit': 'Должен быть целым числом'}
            )
        serializer = SubscribeRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializer.data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )


class UserSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return super(UserSerializer, self).validate(data)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.pk
        ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
