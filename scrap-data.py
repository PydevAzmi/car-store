import os

import django

# Set environment variable > Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from scrapy_data.data import ec_categories, sub_categories
from store.models import Brand, CarModel, CategoryParent

if __name__ == "__main__":
    pass
