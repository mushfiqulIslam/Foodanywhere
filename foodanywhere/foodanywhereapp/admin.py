from django.contrib import admin
from .models import Resturant, Customer, Driver, Meal, Order, OrderDetails

admin.site.register(Resturant)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderDetails)
