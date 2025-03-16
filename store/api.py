# audi = Brand.objects.get(name='Audi')
# audi_parts = Part.objects.filter(compatible_models__brand=audi).distinct()

# bmw = Brand.objects.get(name='BMW')
# three_series = CarModel.objects.get(brand=bmw, name='3 Series')
# car_parts = Part.objects.filter(compatible_models=three_series)

# engine_category = Category.objects.get(slug='engine')
# mercedes_engine_parts = Part.objects.filter(
#     category=engine_category,
#     compatible_models__brand=mercedes
# ).distinct()

from django.shortcuts import get_object_or_404
from rest_framework import filters

from api.utils.response import APIResponse
from api.views import ServerAPIView, ServerModelViewSet

from .models import Brand, CarModel, Category, CategoryParent, Part
from .serializers import (BrandFilterSerializer, CarModelFilterSerializer,
                          CategoryFilterSerializer, PartSerializer,
                          SubCategoryFilterSerializer)


class PartViewSet(ServerModelViewSet):
    """
    A simple ViewSet for listing or retrieving Parts.
    """

    queryset = Part.objects.all()
    serializer_class = PartSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'sku',
        'category',
        'name',
        'compatible_models',
        'compatible_models__brand',
        'oem_number',
    ]
    ordering_fields = ['is_featured', 'quantity', 'price']

    def list(self, request):
        query_filters = {}
        brandId = request.query_params.get('brandId')
        categoryId = request.query_params.get('categoryId')
        compatibleModel = request.query_params.get('compatibleModel')

        if brandId is not None:
            query_filters["compatible_models__brand"] = brandId
        if categoryId is not None:
            query_filters["category"] = categoryId
        if compatibleModel is not None:
            query_filters["compatible_models"] = compatibleModel

        queryset = Part.objects.filter(**query_filters).distinct()
        page_size = request.query_params.get('page_size', 20)
        self.pagination_class.page_size = page_size
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = PartSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PartSerializer(queryset, many=True)
        return APIResponse(data=serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Part.objects.all()
        Part = get_object_or_404(queryset, pk=pk)
        serializer = PartSerializer(Part)
        return APIResponse(data=serializer.data)


part_list = PartViewSet.as_view({'get': 'list'})
part_detail = PartViewSet.as_view({'get': 'retrieve'})


# filters
class SubCategoryFiltersAPIView(ServerAPIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = SubCategoryFilterSerializer(categories, many=True)
        return APIResponse(data=serializer.data)


class CategoryFiltersAPIView(ServerAPIView):
    def get(self, request):
        categories = CategoryParent.objects.all()
        serializer = CategoryFilterSerializer(categories, many=True)
        return APIResponse(data=serializer.data)


class BrandFilterAPIView(ServerAPIView):
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandFilterSerializer(brands, many=True)
        return APIResponse(data=serializer.data)


class CarModelFilterApiView(ServerAPIView):
    def get(self, request):
        brand_id = request.query_params.get('brandId')
        if brand_id:
            car_models = CarModel.objects.filter(brand=brand_id)
        else:
            car_models = CarModel.objects.all()
        serializer = CarModelFilterSerializer(car_models, many=True)
        return APIResponse(data=serializer.data)
