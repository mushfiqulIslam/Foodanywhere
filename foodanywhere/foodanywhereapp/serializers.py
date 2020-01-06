from rest_framework import serializers
from .models import Resturant, Meal

class ResturantSerializer(serializers.ModelSerializer):
    """Serializer class for Resturant"""
    logo = serializers.SerializerMethodField()

    def get_logo(self, resturant):
        request = self.context.get('request')
        logo_url = resturant.logo.url
        return request.build_absolute_uri(logo_url)

    class Meta:
        model = Resturant
        fields = ("id", "name", "phone", "address", "logo")


class MealSerializer(serializers.ModelSerializer):
    """Serializer class for Meal"""
    image = serializers.SerializerMethodField()

    def get_image(self, meal):
        request = self.context.get('request')
        print(request)
        image_url = meal.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = Meal
        fields = ("id", "name", "short_description", "image", "price")
