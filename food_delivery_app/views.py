from django.shortcuts import render, get_object_or_404, redirect
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
from django.utils import timezone
import uuid
from decimal import Decimal
from django.contrib import messages

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
def order_history_view(request, customer_id):


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
    restaurant = get_object_or_404(Restaurants, res_id=restaurant_id)
    menu_items = MenuItems.objects.filter(res=restaurant)
    
    context = {
        "restaurant": restaurant,
        "menu_items": menu_items,
    }
    return render(request, 'restaurant_menu.html', context)

def add_to_cart(request, res_id, item_name):
    restaurant = get_object_or_404(Restaurants, res_id=res_id)
    menu_item = get_object_or_404(MenuItems, res=restaurant, item_name=item_name)
    
    cart = request.session.get('cart', {})
    
    item_key = f"{res_id}_{item_name}"
    
    if item_key in cart:
        cart[item_key]['quantity'] += 1
    else:
        cart[item_key] = {
            'restaurant_id': res_id,
            'item_name': item_name,
            'quantity': 1,
            'price': str(menu_item.price)
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('restaurant_menu', restaurant_id=res_id)

def update_cart(request, item_key):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        quantity = int(request.POST.get('quantity', 0))
        if quantity > 0:
            cart[item_key]['quantity'] = quantity
        else:
            if item_key in cart:
                del cart[item_key]
        
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('show_cart')

def show_cart(request):
    cart = request.session.get('cart', {})
    total = Decimal('0')
    cart_items = []
    
    for item_key, item_data in cart.items():
        price = Decimal(item_data['price'])
        quantity = item_data['quantity']
        subtotal = price * quantity
        
        cart_items.append({
            'key': item_key,
            'name': item_data['item_name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('show_cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('show_cart')
        
    if request.method == 'POST':
        order = Orders.objects.create(
            order_id=str(uuid.uuid4()),
            restaurant_id=next(iter(cart.values()))['restaurant_id'],
            status='pending',
            timestamp=timezone.now()
        )
        
        for item_data in cart.values():
            OrderItems.objects.create(
                order=order,
                item_name=item_data['item_name'],
                quantity=item_data['quantity']
            )
        
        request.session['cart'] = {}
        request.session.modified = True
        
        return render(request, 'checkout_success.html', {'order_id': order.order_id})
    
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'checkout.html', {'total': total})