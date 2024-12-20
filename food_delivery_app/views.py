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
from .models import Customers
from .forms import RegistrationForm, LoginForm

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
    # 从 session 获取 customer_id
    customer_id = request.session.get('user_id')

    if not customer_id:

        return redirect('login')


    restaurants = Restaurants.objects.all()


    return render(request, 'restaurants_list.html', {
        'restaurants': restaurants,
        'customer_id': customer_id,
    })

# TODO: account_view also needs to take customer_id as a parameter
def account_view(request):
    return render(request, 'account.html')


def order_history_view(request):
    customer_id = request.session.get('user_id')


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
    user_id = request.session.get('user_id', None)
    
    if not user_id:
        return redirect('login')
    user = get_object_or_404(Customers, customer_id=user_id)
    
    if request.method == 'POST':
        payment = Payments.objects.create(
            payment_id=str(uuid.uuid4()),
            method="Apple Pay",
            timestamp=timezone.now()
        )

        order = Orders.objects.create(
            order_id=str(uuid.uuid4()),
            customer=user,
            restaurant_id=next(iter(cart.values()))['restaurant_id'],
            status='successfull',
            payment=payment,
            timestamp=timezone.now(),

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

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            last_customer = Customers.objects.order_by('-customer_id').first()
            if last_customer:

                last_id = int(last_customer.customer_id[1:])
                new_customer_id = f'C{last_id + 1:03d}'
            else:

                new_customer_id = 'C001'


            customer = form.save(commit=False)
            customer.customer_id = new_customer_id
            customer.save()

            messages.success(request, "Registration successful! You can now log in.")
            print(f"DEBUG: new user id: {new_customer_id}")
            return redirect('login')
        else:

            print(f"DEBUG: fail to verify form: {form.errors}")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']


            try:
                customer = Customers.objects.get(username=username_or_email)
            except Customers.DoesNotExist:
                try:
                    customer = Customers.objects.get(email=username_or_email)
                except Customers.DoesNotExist:
                    # 用户不存在
                    messages.error(request, "User does not exist.")
                    return render(request, 'login.html', {'form': form})


            if password == customer.password:

                request.session['user_id'] = customer.customer_id

                return redirect('restaurant_list')
            else:
                messages.error(request, "Username and password do not match, please try again.")
        else:

            if not form.cleaned_data.get('username'):
                messages.error(request, "Please enter your username.")
            if not form.cleaned_data.get('password'):
                messages.error(request, "Please enter your password.")
            print(f"DEBUG: fail to verify form: {form.errors}")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def profile(request, customer_id):

    session_user_id = request.session.get('user_id')  # 从 session 获取 user_id
    if not session_user_id:
        messages.error(request, "You need to log in to view your profile.")
        print("DEBUG: User is not logged in. Redirecting to login.")
        return redirect('login')


    if session_user_id != customer_id:
        messages.error(request, "You are not authorized to view this profile.")
        print(f"DEBUG: Unauthorized access attempt. Session user_id: {session_user_id}, URL customer_id: {customer_id}")
        return redirect('home')

    try:

        customer = Customers.objects.get(customer_id=customer_id)
    except Customers.DoesNotExist:
        messages.error(request, "User not found.")
        print(f"DEBUG: No customer found with ID: {customer_id}")
        return redirect('home')

    if request.method == 'POST':

        fields_to_update = ['fname', 'lname', 'street', 'city', 'state', 'zipcode', 'phone']
        for field in fields_to_update:
            setattr(customer, field, request.POST.get(field, getattr(customer, field)))


        customer.save()
        messages.success(request, "Your profile has been updated successfully.")
        print("DEBUG: User profile updated.")


    print(f"DEBUG: Customer loaded: {customer}")
    context = {
        'username': customer.username,
        'email': customer.email,
        'fname': customer.fname or '',
        'lname': customer.lname or '',
        'street': customer.street or '',
        'city': customer.city or '',
        'state': customer.state or '',
        'zipcode': customer.zipcode or '',
        'phone': customer.phone or '',
    }
    return render(request, 'profile.html', context)

def logout_view(request):
    request.session.flush()
    return redirect('login')

def home(request):
    return render(request, 'home.html')