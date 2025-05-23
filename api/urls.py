from decouple import config
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from .views import GetIpAddress

schema_view = get_schema_view(
    openapi.Info(
        title="Medshel API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=config('EMAIL_HOST_USER')),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        'swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("auth/", include("accounts.urls", namespace="accounts")),
    path("store/", include("store.urls", namespace="store")),
    path("get-ip/",GetIpAddress.as_view(), name="get-ip")
]
