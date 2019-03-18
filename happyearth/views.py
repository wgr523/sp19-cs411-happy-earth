from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse
from .models import *

def fake_index(request):
    return HttpResponse("Happy, earth!")

def fake_user(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        try:
            user = User.objects.get(name=username)
        except User.DoesNotExist:
            return HttpResponse('User not in db!')
        return HttpResponse('Hi, '+username+'! your phone is '+user.phone+'<p><a href="'+reverse('logout')+'">LOGOUT</a></p>')
    else:
        return HttpResponse("Happy, earth!")
## def restaurants(request):
##     restaurant_list = Restaurant.objects.values()
##     context = {'restaurant_list': restaurant_list}
##     return render(request, 'happyearth/restaurants.html', context)

class RestaurantIndex(generic.ListView):
    context_object_name = 'restaurant_list'
    def get_queryset(self):
        """Return the last five published questions."""
        return Restaurant.objects.values()

class UserIndex(generic.ListView):
    context_object_name = 'user_list'
    def get_queryset(self):
        return User.objects.values()
    
class DishIndex(generic.ListView):
    context_object_name = 'dish_list'
    def get_queryset(self):
        return Dish.objects.values()
    
class FavoritesIndex(generic.ListView):
    context_object_name = 'favorites_list'
    def get_queryset(self):
        return Favorites.objects.values()
