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
    # TODO: needs to get customer_id through session
    restaurants = Restaurants.objects.all()
    return render(request, 'restaurants_list.html', {'restaurants': restaurants})

# TODO: account_view also needs to take customer_id as a parameter
def account_view(request):
    return render(request, 'account.html')


# TODO: order history also needs to take customer_id as a parameter
def order_history(request, customer_id):

    # Fetch all orders for the customer, and join related restaurant, driver, and payment
    orders = Orders.objects.filter(customer_id=customer_id).select_related(
        'customer',   # ForeignKey to Customers model
        'restaurant', # ForeignKey to Restaurants model
        'driver',     # ForeignKey to Drivers model
        'payment'     # ForeignKey to Payments model
    )

    # Prepare the context with related data
    order_history = []

    for order in orders:
    # Fetch all related OrderItems for the current order
        order_items = OrderItems.objects.filter(order=order)
        for item in order_items:
            # Fetch price from MenuItems model based on the item name and restaurant
            menu_item = MenuItems.objects.filter(res=order.restaurant, item_name=item.item_name).first()
            item_price = menu_item.price if menu_item else 0  # Default to 0 if no price is found
        
            order_history.append({
                'order_id': order.order_id,
                'customer_name': f"{order.customer.fname} {order.customer.lname}",
                'restaurant_name': order.restaurant.name,  # Using the related restaurant name
                'driver_name': order.driver.name if order.driver else 'N/A',  # Using the related driver name
                'status': order.status,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'price': f"${item_price * item.quantity:.2f}",  # Calculate the total price for the item
                'payment_method': order.payment.method,
                'customer_address': f"{order.customer.street}, {order.customer.city}, {order.customer.state}, {order.customer.zipcode}",
                'order_time': order.timestamp.strftime("%Y-%m-%d %I:%M %p"),
                'estimated_arrival': order.estimated_arrival.strftime("%Y-%m-%d %I:%M %p") if order.estimated_arrival else 'N/A',
            })

    # Pass the data to the template
    context = {
        'orders': order_history
    }
    return render(request, 'order_history.html', context)

def restaurant_menu(request, restaurant_id):
    # Assuming there is a related menu item model, you would query it here
    menu_items = MenuItems.objects.all().filter(res=restaurant_id)  # Replace with actual related model name if different
    return render(request, 'restaurant_menu.html', { 'menu_items': menu_items})