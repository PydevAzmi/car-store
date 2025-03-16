from rest_framework import permissions


class IsTraderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow traders to edit/create/delete.
    Others can only view.
    """

    def has_permission(self, request, view):
        # Allow anyone to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is authenticated and is_trader
        return request.user.is_authenticated and request.user.is_trader

    def has_object_permission(self, request, view, obj):
        # Allow anyone to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is authenticated and is_trader
        return request.user.is_authenticated and request.user.is_trader


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow anyone to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if user is authenticated and is the owner of the object
        return request.user.is_authenticated and obj.user == request.user
