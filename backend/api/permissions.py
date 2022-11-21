from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticated)


class IsOwnerProfile(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff
        )


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
