from django.urls import include, path

from .api import Test

app_name = 'store'

urlpatterns = [
    path('test/', Test.as_view(), name="test"),
]
