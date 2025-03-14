from django.urls import path, include
from .api import Test
app_name = 'store'

urlpatterns = [
    path('test/', Test.as_view(), name="test"),
]
