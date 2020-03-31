import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from django.utils import timezone
from django.http import JsonResponse
from braces.views import CsrfExemptMixin
from oauth2_provider.models import AccessToken
from .models import Resturant, Meal, Order, OrderDetails, Driver
from .serializers import ResturantSerializer, MealSerializer, OrderSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta


##################
#Customer Section#
##################

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



class CustomerOrderAdd(CsrfExemptMixin, APIView):
    """working with the order"""
    authentication_classes = []

    def post(self, request):
        """params:
                access_token
                resturant_id
                address
                order_details
                stripe_token
                return {'status'}
        """
        access_token = AccessToken.objects.get(token=request.data.get("access_token"),
            expires__gt=timezone.now())
        customer = access_token.user.customer
        if Order.objects.filter(customer=customer).exclude(status=Order.DELIVERED):
            return JsonResponse({"status": "failed",
                "error": "Last order haas not been delivered yet"})
        if not request.POST["address"]:
            return JsonResponse({"status": "failed", "error": "Address needed"})

        order_details = json.loads(request.POST["order_details"])
        total_price = 0
        for meal in order_details:
            total_price += Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"]

        if len(order_details) > 0:
            order = Order.objects.create(
                customer = customer,
                resturant_id = request.POST["resturant_id"],
                total = total_price,
                status = Order.COOKING,
                address = request.POST["address"]
            )

        for meal in order_details:
            OrderDetails.objects.create(
                order = order,
                meal_id = meal["meal_id"],
                quantity = meal["quantity"],
                sub_total = Meal.objects.get(id=meal["meal_id"]).price * meal["quantity"]
            )
        return JsonResponse({"status":"success"})


class CustomerLatestOrder(APIView):

    def get(self, request, *args, **kwargs):
        access_token = AccessToken.objects.get(token=request.GET["access_token"],
            expires__gt=timezone.now())
        customer = access_token.user.customer
        order = OrderSerializer(Order.objects.filter(customer=customer).last()).data
        return JsonResponse({'order':order})

###################
#Resturant Section#
###################

class ResturantOrderNotification(APIView):

    def get(self, request, last_request_time, *args, **kwargs):
        notification = Order.objects.filter(resturant=request.user.resturant,
            create_at__gt=last_request_time).count()
        return JsonResponse({'notification': notification})

##################
# Driver Section #
##################

class DriverReadyOrder(APIView):
    """docstring for ."""
    def get(self, request, *args, **kwargs):
        orders = OrderSerializer(
            Order.objects.filter(status=Order.READY, driver=None).order_by("-id"),
            many=True
        ).data
        return JsonResponse({'orders':orders})


class DriverPickOrder(APIView):
    """docstring for ."""
    @method_decorator(csrf_exempt)
    #params: access_token, order_id
    def post(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.data.get('access_token'),
            expires__gt=timezone.now())
        # Get driver
        driver = access_token.user.driver
        if Order.objects.filter(driver=driver).exclude(status=Order.ONTHEWAY):
                return JsonResponse({"status" : "failed",
                                    "error" : "You can only pick one order"})

        try:
            order = Order.objects.get(
                    id = request.POST["order_id"],
                    driver = None,
                    status = Order.READY
                    )
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()
            return JsonResponse({"status":"succes"})
        except Order.DoesNotExist:
            return JsonResponse({"status" : "failed",
                                "error" : "This order has been picked up by another driver"})
        return JsonResponse({})


class DriverRecentOrder(APIView):
    """docstring for ."""
    #params: access_token
    def get(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.GET.get('access_token'),
            expires__gt=timezone.now())
        # Get driver
        driver = access_token.user.driver
        order = OrderSerializer(
                Order.objects.filter(driver=driver).order_by("picked_at").last()
        ).data
        return JsonResponse({"order": order})


class DriverCompleteOrder(APIView):
    """docstring for ."""
    @method_decorator(csrf_exempt)
    #params: access_token, order_id
    def post(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.data.get('access_token'),
            expires__gt=timezone.now())
        # Get driver
        driver = access_token.user.driver
        order = Order.objects.get(id=request.POST["order_id"], driver= driver)
        order.status = order.DELIVERED
        order.save()
        return JsonResponse({"status": "completed"})


class DriverRevenue(APIView):
    """docstring for ."""
    #params: access_token
    def get(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.GET.get('access_token'),
            expires__gt=timezone.now())
        # Get driver
        driver = access_token.user.driver
        revenue =  {}
        today = timezone.now()
        current_weekdays = [today + timedelta(days=i)for i in range(
                            0 - today.weekday(), 7 - today.weekday()
        )]

        for day in current_weekdays:
            orders = Order.objects.filter(
                    driver = driver,
                    status = Order.DELIVERED,
                    picked_at__year = day.year,
                    picked_at__month = day.month,
                    picked_at__day = day.day
            )

            revenue[day.strftime("%a")] = sum(order.total for order in orders)
            for order in orders:
                print(order.customer)
                print(order.total)


        return JsonResponse({"revenue" : revenue})


class DriverLocation(APIView):
    """docstring for ."""
    #params: access_token
    def get(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.GET.get('access_token'),
            expires__gt=timezone.now())
        # Get driver location
        customer = access_token.user.customer
        current_order = Order.objects.filter(customer=customer, status=Order.ONTHEWAY).last()
        location = current_order.driver.location
        return JsonResponse({"location": location})


class DriverLocationUpdate(APIView):
    """docstring for ."""
    @method_decorator(csrf_exempt)
    #params: access_token, latitude, longitude
    def post(self, request, *args, **kwargs):
        # Get token
        access_token = AccessToken.objects.get(token=request.POST['access_token'],
            expires__gt=timezone.now())
        # Get driver
        driver = access_token.user.driver
        #Set location
        driver.location = request.POST['location']
        driver.save()
        return JsonResponse({"status": "success"})


##################
# Stripe Section #
##################

# class DriverLocationUpdate(APIView):
