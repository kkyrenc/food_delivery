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
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customers
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.hashers import check_password


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # 生成新的 customer_id
            last_customer = Customers.objects.order_by('-customer_id').first()  # 获取最后一个用户
            if last_customer:
                # 提取最后一个 ID 的数字部分，递增后生成新的 ID
                last_id = int(last_customer.customer_id[1:])
                new_customer_id = f'C{last_id + 1:03d}'
            else:
                # 如果没有任何用户记录，从 C001 开始
                new_customer_id = 'C001'

            # 保存表单并设置 customer_id
            customer = form.save(commit=False)
            customer.customer_id = new_customer_id  # 为新用户分配 ID
            customer.save()  # 保存到数据库

            messages.success(request, "Registration successful! You can now log in.")
            print(f"DEBUG: 表单验证通过，新用户 ID: {new_customer_id}")
            return redirect('login')
        else:
            # 如果验证失败，输出调试信息
            print(f"DEBUG: 表单验证失败: {form.errors}")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # 获取用户输入
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # 查找用户
            try:
                customer = Customers.objects.get(username=username_or_email)
            except Customers.DoesNotExist:
                try:
                    customer = Customers.objects.get(email=username_or_email)
                except Customers.DoesNotExist:
                    # 用户不存在
                    messages.error(request, "User does not exist.")
                    return render(request, 'login.html', {'form': form})

            # 验证密码
            if password == customer.password:  # 明文密码对比
                # 保存用户登录状态到 session
                request.session['user_id'] = customer.customer_id
                # messages.success(request, f"Welcome back, {customer.fname}!")
                return redirect('home')  # 跳转到主页
            else:
                messages.error(request, "Username and password do not match, please try again.")
        else:
            # 表单验证失败，检查字段是否为空
            if not form.cleaned_data.get('username'):
                messages.error(request, "Please enter your username.")
            if not form.cleaned_data.get('password'):
                messages.error(request, "Please enter your password.")
            print(f"DEBUG: 表单验证失败: {form.errors}")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def profile(request, customer_id):
    # 检查用户是否已登录
    session_user_id = request.session.get('user_id')  # 从 session 获取 user_id
    if not session_user_id:
        messages.error(request, "You need to log in to view your profile.")
        print("DEBUG: User is not logged in. Redirecting to login.")
        return redirect('login')

    # 确保 URL 中的 customer_id 与 session 中的 user_id 匹配
    if session_user_id != customer_id:
        messages.error(request, "You are not authorized to view this profile.")
        print(f"DEBUG: Unauthorized access attempt. Session user_id: {session_user_id}, URL customer_id: {customer_id}")
        return redirect('home')

    try:
        # 根据 customer_id 获取用户信息
        customer = Customers.objects.get(customer_id=customer_id)
    except Customers.DoesNotExist:
        messages.error(request, "User not found.")
        print(f"DEBUG: No customer found with ID: {customer_id}")
        return redirect('home')

    if request.method == 'POST':
        # 获取所有字段的更新值
        fields_to_update = ['fname', 'lname', 'street', 'city', 'state', 'zipcode', 'phone']
        for field in fields_to_update:
            setattr(customer, field, request.POST.get(field, getattr(customer, field)))

        # 保存更新后的数据
        customer.save()
        messages.success(request, "Your profile has been updated successfully.")
        print("DEBUG: User profile updated.")

    # 将用户信息传递给模板
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
def home(request):
    return render(request, 'home.html')