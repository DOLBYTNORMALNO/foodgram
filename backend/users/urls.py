from django.urls import include, path

from .views import AvatarView, SubscriptionsView, SubcribeView

app_name = 'users'

urlpatterns = [
    path(
        'users/subscriptions/', SubscriptionsView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:pk>/subscribe/', SubcribeView.as_view(), name='subscribe'
    ),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
