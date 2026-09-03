from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Follow
from .serializers import (
    FollowSerializer,
    SetAvatarSerializer,
)


class SubscriptionsView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class SubcribeView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowSerializer

    def post(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if author == user:
            return Response(
                {'errors': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Повторная подписка недопустима'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if author == user:
            return Response(
                {'errors': 'Нельзя отписаться от себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на данного автора'},
            status=status.HTTP_400_BAD_REQUEST
        )


class AvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = SetAvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar = request.user.avatar
        avatar_url = (
            request.build_absolute_uri(avatar.url) if avatar else None
        )
        return Response({'avatar': avatar_url})

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
