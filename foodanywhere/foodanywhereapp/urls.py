from django.urls import path
from . import views, apis
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('resturant/', views.ResturantHome.as_view(), name='resturant-home'),
    path('resturant/sign-in/', auth_views.LoginView.as_view(template_name='resturant/sign_in.html'),
        name = 'resturant-sign-in'),
    path('resturant/sign-out/', auth_views.LogoutView.as_view(next_page='/'),
        name = 'resturant-sign-out'),
    path('resturant/sign-up/', views.ResturantSignUp.as_view(), name = 'resturant-sign-up'),
    path('resturant/account/', views.ResturantAccount.as_view(), name = 'resturant-account'),
    #meal
    path('resturant/meal/', views.ResturantMeal.as_view(), name = 'resturant-meal'),
    path('resturant/meal/add/', views.ResturantAddMeal.as_view(), name = 'resturant-add-meal'),
    path('resturant/meal/edit/<int:pk>/', views.ResturantEditMeal.as_view(), name = 'resturant-edit-meal'),

    path('resturant/order/', views.ResturantOrder.as_view(), name = 'resturant-order'),
    path('resturant/report/', views.ResturantReport.as_view(), name = 'resturant-report'),

    #APIs for Customer
    path('api/customer/resturants/', apis.CustomerResturants.as_view()),
    path('api/customer/<int:resturant_id>/meals/', apis.CustomerMeals.as_view()),
    path('api/customer/order/add/', apis.CustomerOrderAdd.as_view()),
    path('api/resturant/order/notification/<str:last_request_time>/', apis.ResturantOrderNotification.as_view(), name = 'resturant-notification'),
    path('api/customer/order/latest/', apis.CustomerLatestOrder.as_view()),
    path('api/customer/driver/location/', apis.DriverLocation.as_view()),

    #APIs for Drivers
    path('api/driver/orders/ready/', apis.DriverReadyOrder.as_view()),
    path('api/driver/orders/pick/', apis.DriverPickOrder.as_view()),
    path('api/driver/orders/latest/', apis.DriverRecentOrder.as_view()),
    path('api/driver/orders/complete/', apis.DriverCompleteOrder.as_view()),
    path('api/driver/revenue/', apis.DriverRevenue.as_view()),
    path('api/driver/location/update/', apis.DriverLocationUpdate.as_view()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
