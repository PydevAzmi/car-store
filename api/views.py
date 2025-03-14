from rest_framework import permissions, views

class ServerAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated ]

class PublicServerAPIView(ServerAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
