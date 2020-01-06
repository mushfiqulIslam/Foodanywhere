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
    path('api/customer/order/add/', apis.CustomerOrder.as_view()),
    path('api/customer/order/latest/', apis.CustomerOrder.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
