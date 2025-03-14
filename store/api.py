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


from api.utils.response import APIResponse
from api.views import ServerAPIView, PublicServerAPIView

class Test(ServerAPIView):
    def get(self, request):
        return APIResponse(data='working')