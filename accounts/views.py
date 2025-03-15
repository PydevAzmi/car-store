from django.conf import settings
from djoser.views import UserViewSet
from rest_framework.response import Response

# Create your views here.


class CustomUserViewSet(UserViewSet):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=204, data={"detail": "User deleted successfully"})
