import json
from .models import *
from django.core.exceptions import ObjectDoesNotExist


def cookieCart(request):
    
    try: 
        cart = json.loads(request.COOKIES['cart'])
    except: 
        cart = {}
        
    print('Cart:', cart)
    items = [] #empty list
    order = {'get_cart_total':0, 'get_cart_items':0} #in case we're logged out (eviter l'erreur) we create an image
    cartItems = order['get_cart_items']
        
    for i in cart:
            #we use try block to prevent items in cart that may have been removed from admin 
        try:
            cartItems += cart[i]['quantity']
            
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)
            
            if product.digital == False :
                order['shipping'] = True
        except:
            pass
    return {'cartItems': cartItems, 'order':order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
           customer, created = Customer.objects.get_or_create(user=request.user, email=request.user.email, name=request.user.username)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order':order, 'items':items}

def guestOrder(request, data):
    
    print('User is not logged in..')
        
    print('COOKIES:', request.COOKIES)
    
    name = data['form']['name']
    email = data['form']['email']
    #we use this to get the data and create that cart for out quest user
    cookieData = cookieCart(request)
    items = cookieData['items']
    #the guest user doesn't need to create new email every time he wants to do an order
    customer, created = Customer.objects.get_or_create(
        email= email,
    )
    customer.name = name
    customer.save()
        
    order = Order.objects.create(
        customer= customer,
        complete=False,
    )
    #add the items to the database
    for item in items:
        #create the product
        product = Product.objects.get(id=item['product']['id'])
        #create the order item
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        )
    return customer, order      