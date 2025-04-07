from requests import Response
from rest_framework import permissions, views, viewsets
from rest_framework.pagination import PageNumberPagination

from api.utils.response import APIResponse
from rest_framework import status
from .permissions import IsOwnerOrReadOnly, IsTraderOrReadOnly


class ServerModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination


class ServerAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DashboardModelViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsTraderOrReadOnly,
        IsOwnerOrReadOnly,
    ]


class DashboardAPIView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsTraderOrReadOnly,
        IsOwnerOrReadOnly,
    ]


class PublucModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]


class PublicServerAPIView(ServerAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]


class GetIpAddress(PublicServerAPIView):
    """
    Get the IP address of the client.
    """

    def get(self, request, *args, **kwargs):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return APIResponse(data={"ip": ip})