from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (BrandFilterAPIView, CarModelFilterApiView,
                  CategoryFiltersAPIView, PartViewSet,
                  SubCategoryFiltersAPIView)

app_name = 'store'

router = DefaultRouter()
router.register(r'parts', PartViewSet, basename='part')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'filters/categories/', CategoryFiltersAPIView.as_view(), name='category-filters'
    ),
    path(
        'filters/sub-categories/',
        SubCategoryFiltersAPIView.as_view(),
        name='sub-category-filters',
    ),
    path(
        'filters/brands/',
        BrandFilterAPIView.as_view(),
        name='brand-filters',
    ),
    path(
        'filters/car-models/',
        CarModelFilterApiView.as_view(),
        name='car-models-filters',
    ),
]
