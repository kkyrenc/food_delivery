from django.shortcuts import render
from .models import (
    Cars,
    Customers,
    Drivers,
    EmergencyContacts,
    Members,
    MenuItems,
    OrderItems,
    Orders,
    Payments,
    Restaurants,
    Reviews,
)


# Create your views here.
def test_mysql(request):
    # Use a customer to test
    customers = Customers.objects.all()
    customer = customers[0]
    context = {
        'first_name': customer.fname,
        'last_name': customer.lname,
        'address': f'{customer.street}, {customer.city}, {customer.state}, {customer.zipcode}',
        'phone': customer.phone
    }
    return render(request, 'home.html', context)


def restaurant_list(request):
    restaurants = Restaurants.objects.all()
    return render(request, 'restaurants_list.html', {'restaurants': restaurants})

def account_view(request):
    return render(request, 'account.html')

def order_history_view(request):
    return render(request, 'order_history.html')

def restaurant_menu(request, restaurant_id):
    # Assuming there is a related menu item model, you would query it here
    menu_items = MenuItems.objects.all().filter(res=restaurant_id)  # Replace with actual related model name if different
    return render(request, 'restaurant_menu.html', { 'menu_items': menu_items})