from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from .models import Meal, Order, Driver
from .forms import UserForm, ResturantForm, UserFormForEdit, MealForm
from django.contrib.auth.models import User
from multi_form_view import MultiModelFormView
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Case, When


class Home(RedirectView):
    '''
    Home Page
    '''
    pattern_name = 'resturant-home'


class ResturantHome(LoginRequiredMixin, RedirectView):
    '''
    Home Page
    '''
    login_url = 'resturant-sign-in'
    pattern_name = 'resturant-order'


class ResturantSignUp(MultiModelFormView):
    form_classes = {
        'user_form' : UserForm,
        'resturant_form' : ResturantForm,
    }

    template_name = 'resturant/sign_up.html'

    def get_form_kwargs(self):
        kwargs = super(ResturantSignUp, self).get_form_kwargs()
        kwargs['user_form']['prefix'] = 'user'
        kwargs['resturant_form']['prefix'] = 'resturant'
        return kwargs

    def forms_valid(self, forms):
        UserForm = forms['user_form']
        u = UserForm.cleaned_data
        user = User.objects.create_user(username=u['username'],
                                        password=u['password'],
                                        first_name=u['first_name'],
                                        last_name=u['last_name'],
                                        email=u['email'])
        resturant = forms['resturant_form'].save(commit=False)
        resturant.user = user
        resturant.save()
        return redirect('resturant-home')


class ResturantAccount(LoginRequiredMixin, TemplateView):
    """docstring for ."""
    login_url = 'resturant-sign-in'
    template_name = 'resturant/account.html'

    def get(self, request, *args, **kwargs):
        user_form = UserFormForEdit(instance=request.user)
        resturant_form = ResturantForm(instance=request.user.resturant)
        return render(request, self.template_name, {
            'user_form': user_form,
            'resturant_form': resturant_form
        })

    def post(self, request, *args, **kwargs):
        user_form = UserFormForEdit(request.POST, instance=request.user)
        resturant_form = ResturantForm(request.POST, request.FILES, instance=request.user.resturant)

        if user_form.is_valid() and resturant_form.is_valid():
            user_form.save()
            resturant_form.save()

        return render(request, self.template_name, {
            'user_form': user_form,
            'resturant_form': resturant_form
        })


class ResturantMeal(LoginRequiredMixin, ListView):
    """showing meal of resturant"""

    login_url = 'resturant-sign-in'
    template_name = 'resturant/meal.html'
    model = Meal
    context_object_name = 'meals'

    def get_queryset(self):
        return Meal.objects.filter(resturant=self.request.user.resturant)


class ResturantAddMeal(LoginRequiredMixin, FormView):
    """docstring for ."""

    login_url = 'resturant-sign-in'
    template_name = 'resturant/add_meal.html'
    form_class = MealForm

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        meal = form.save(commit=False)
        meal.resturant = self.request.user.resturant
        meal.save()
        return redirect('resturant-meal')


class ResturantEditMeal(LoginRequiredMixin, UpdateView):
    """docstring for ."""

    login_url = 'resturant-sign-in'
    template_name = 'resturant/edit_meal.html'
    model = Meal
    fields = ("name", "short_description", "image", "price")
    success_url = reverse_lazy('resturant-meal')


class ResturantOrder(LoginRequiredMixin, TemplateView):
    """showing order of resturant"""

    login_url = 'resturant-sign-in'
    template_name = 'resturant/order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.filter(resturant=self.request.user.resturant).order_by("-id")
        return context

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=request.POST["id"], resturant=request.user.resturant)
        if order.status == Order.COOKING:
            order.status = order.READY
            order.save()
        order = Order.objects.filter(resturant=self.request.user.resturant).order_by("-id")
        return render(request, self.template_name, {
            'order': order,
        })


class ResturantReport(LoginRequiredMixin, TemplateView):
    """showing report of resturant by calculating revenue and number of order by current week"""

    login_url = 'resturant-sign-in'
    template_name = 'resturant/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        revenue = []
        orders = []

        today = datetime.now()
        current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

        for day in current_weekdays:
            delivered_orders = Order.objects.filter(
                resturant = self.request.user.resturant,
                status = Order.DELIVERED,
                create_at__year = day.year,
                create_at__month = day.month,
                create_at__day = day.day
            )
            revenue.append(sum(order.total for order in delivered_orders))
            orders.append(delivered_orders.count())

        context['revenue'] = revenue
        context['orders'] = orders
        # Top 3 Meals
        top3_meals = Meal.objects.filter(resturant = self.request.user.resturant)\
                     .annotate(total_order = Sum('orderdetails__quantity'))\
                     .order_by("-total_order")[:3]

        meal = {
            "labels": [meal.name for meal in top3_meals],
            "data": [meal.total_order or 0 for meal in top3_meals]
            }
        context['meal'] = meal
        return context
