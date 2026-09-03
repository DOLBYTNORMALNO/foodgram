from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow
from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
)
from .models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient
        read_only_fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag
        read_only_fields = ('id', 'name', 'slug')


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj.pk).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=('ingredient', 'recipe')
            )
        ]


class RecipeListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user.id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user.id,
            recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeListSerializer(
            instance,
            context={'request': request}
        )
        return serializer.data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if not ingredients_data:
            raise serializers.ValidationError('нужен хотя бы один ингредиент')
        elif not tags_data:
            raise serializers.ValidationError('нужен хотя бы один тег')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        ingredient_instances = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_instances)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data:
            instance.tags.set(tags_data)

        if ingredients_data:
            IngredientRecipe.objects.filter(recipe=instance).delete()
            ingredient_instances = [
                IngredientRecipe(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients_data
            ]
            IngredientRecipe.objects.bulk_create(ingredient_instances)

        return instance

    def validate(self, data):
        required = ('ingredients', 'tags', 'image', 'name', 'text',
                    'cooking_time')
        if self.instance is not None:
            missing = [f for f in required if f not in self.initial_data]
            if missing:
                raise serializers.ValidationError(
                    {f: 'Обязательное поле.' for f in missing}
                )
        ingredient_data = self.initial_data.get('ingredients')
        if ingredient_data is not None and not ingredient_data:
            raise serializers.ValidationError(
                {'ingredients': 'Нужен хотя бы один ингредиент.'}
            )
        if ingredient_data:
            checked_ingredients = set()
            for ingredient in ingredient_data:
                ingredient_obj = get_object_or_404(
                    Ingredient, id=ingredient['id']
                )
                if ingredient_obj in checked_ingredients:
                    raise serializers.ValidationError('дубликат ингредиента')
                checked_ingredients.add(ingredient_obj)
        tags_data = self.initial_data.get('tags')
        if tags_data is not None and not tags_data:
            raise serializers.ValidationError(
                {'tags': 'Нужен хотя бы один тег.'}
            )
        if tags_data and len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError('дубликат тега')
        return data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
