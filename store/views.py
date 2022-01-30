from django.shortcuts import render
from numpy import product
from .models import *
from django.http import JsonResponse
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout 
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib import messages

import json
import datetime

def search(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == "POST":
        searched = request.POST['searched']
        products = Product.objects.filter(name__contains=searched)
        return render(request, 'store/search.html', {'searched':searched, 'products':products, 'cartItems': cartItems})
    else:   
        return render(request, 'store/search.html', {'cartItems': cartItems})

def product_detail(request, slug):
    data = cartData(request)
    cartItems = data['cartItems']
    product = Product.objects.get(slug=slug)
    return render(request, 'store/product_detail.html',{'product':product, 'cartItems': cartItems})        

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("store")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="store/register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("store")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="store/login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("store")

def store(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
                
        
    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    #set the value of data that response
    data = json.loads(request.body)
    ProductId = data['productId']
    action = data['action']
    
    print('Action:', action)
    print('Product:', ProductId)
    
    customer = request.user.customer
    product = Product.objects.get(id=ProductId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif  action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
            
    else:
        customer, order = guestOrder(request, data) 
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    #to make sure that the user can't change the price for example from frontend js or console
    if total == float(order.get_cart_total):
        order.complete = True
        print('dkhlat')
    order.save()
    
    #if shipping is true
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            #attribute from shippingItem
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
                
         )       
            
    return JsonResponse('Payment submitted..', safe=False)
        