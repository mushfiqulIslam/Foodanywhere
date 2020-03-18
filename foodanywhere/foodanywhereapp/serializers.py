from rest_framework import serializers
from .models import Resturant, Meal, Customer, Driver, Order, OrderDetails

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


class OrderCustomerSerializer(serializers.ModelSerializer):
    """Serializer class for Customer of each Order"""
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Customer
        fields = ("id", "name", "avatar", "phone", "address")


class OrderDriverSerializer(serializers.ModelSerializer):
    """Serializer class for Driver of each Order"""
    name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Driver
        fields = ("id", "name", "avatar", "phone", "address")


class OrderResturantSerializer(serializers.ModelSerializer):
    """Serializer class for Resturant of each Order"""

    class Meta:
        model = Resturant
        fields = ("id", "name", "phone", "address")


class OrderMealSerializer(serializers.ModelSerializer):
    """Serializer class for Meal of each Order"""

    class Meta:
        model = Meal
        fields = ("id", "name", "price")


class OrderDetailsSerializer(serializers.ModelSerializer):
    """Serializer class for Order Meal"""
    meal = OrderMealSerializer

    class Meta:
        model = OrderDetails
        fields = ("id", "meal", "quantity", "sub_total")


class OrderSerializer(serializers.ModelSerializer):
    """Serializer class for Order """
    customer = OrderCustomerSerializer()
    resturant = OrderResturantSerializer()
    driver = OrderDriverSerializer()
    order_details = OrderDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source="get_status_display")

    class Meta:
        model = Order
        fields = ("id", "customer", "resturant", "driver", "order_details",
            "total", "status", "address")
