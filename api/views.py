from rest_framework import permissions, views, viewsets
from rest_framework.pagination import PageNumberPagination

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
