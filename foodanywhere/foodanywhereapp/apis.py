from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from django.http import JsonResponse
from rest_framework.response import Response
from .models import Resturant, Meal
from .serializers import ResturantSerializer, MealSerializer

class CustomerResturants(ListModelMixin, GenericAPIView):
    """showing all the resturants information"""
    queryset = Resturant.objects.all()
    serializer_class = ResturantSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CustomerMeals(ListModelMixin, GenericAPIView):
    """showing all the resturants meals"""
    serializer_class = MealSerializer

    def get_queryset(self, resturant_id):
        return Meal.objects.filter(resturant_id=resturant_id).order_by("-id")

    def list(self, request, resturant_id):
        queryset = self.get_queryset(resturant_id)
        serializer = MealSerializer(queryset, many=True, context={"request":request})
        return JsonResponse(serializer.data, safe=False)

    def get(self, request, resturant_id, *args, **kwargs):
        return self.list(request, resturant_id, *args, **kwargs)



class CustomerOrder(GenericAPIView):
    """working wwith the order"""
    pass
