from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_foodgram.views import (SubscriptionCreateDeleteView,
                                SubscriptionListView)
from users.views import CustomUserView

users = DefaultRouter()

users.register(
    r'users/subscriptions', SubscriptionListView, basename='subscriptions')
users.register('users', CustomUserView, basename='users')
urlpatterns = [
    path('users/<id>/subscribe/', SubscriptionCreateDeleteView.as_view()),
    path('', include(users.urls)),
]
