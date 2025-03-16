# PartSerializer, CategorySerializer, BrandSerializer, CarModelSerializer
from rest_framework import serializers

from .models import Brand, CarModel, Category, CategoryParent, Part, PartImage


class ImageSerializer(serializers.Serializer):
    class Meta:
        model = PartImage
        fields = ['id', 'image', 'caption']


class PartSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Part
        fields = [
            'id',
            'name',
            'description',
            'images',
            'sku',
            'oem_number',
            'warranty_months',
            'price',
            'low_stock_threshold',
            'quantity',
            'is_featured',
            'category__name',
            'category_parent__name',
            'trader__company_name',
            'created_at',
            'updated_at',
        ]


class CategoryFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryParent
        fields = ['id', 'name', 'slug']


class SubCategoryFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'slug']


class BrandFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


class CarModelFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ['id', 'name', 'brand']


class CategoryParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryParent
        fields = '__all__'
