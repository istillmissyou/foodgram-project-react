from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)

from api.paginators import PageLimitPagination
from api.serializers import FollowSerializer, SubscriptionSerializer
from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    lookup_field = 'id'
    search_fields = ('username',)

    @action(
        methods=('get',),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def get_self_page(self, request):
        return Response(
            self.get_serializer(request.user).data,
            status=HTTP_200_OK,
        )

    @action(
        methods=('get',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def get_subscriptions(self, request):
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        return self.get_paginated_response(SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        ).data)

    @action(
        methods=('post', 'delete'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        get_object_or_404(
            Subscription,
            user=user,
            author=get_object_or_404(User, id=id)
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)
