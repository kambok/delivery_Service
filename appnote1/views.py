from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from .form import *
from django.forms import inlineformset_factory
from .filters import OrderFilters
from .form import OrderForm,CreateUserForm
from .filters import OrderFilters
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorator import unauthenticated_user,allowed_users,admin_only
from django.contrib.auth.models import Group




@login_required(login_url='login')
@admin_only
def home(request):

    orders=Order.objects.all()
    customers=Customer.objects.all()
    total_orders=orders.count()
    total_customers=customers.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='pending').count()

    context={'orders':orders,'customers':customers,'delivered':delivered,'pending':pending,'total_orders':total_orders,
             'total_customers':total_customers}
    
    return render(request,'appnote1/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk):
    customer=Customer.objects.get(id=pk)
    orders=customer.order_set.all()
    order_count=orders.count()

    myfilters=OrderFilters(request.GET,queryset=orders)
    orders=myfilters.qs
    context={'customers':customer,'orders':orders,'orders_count':order_count,'myfilters':myfilters}
    
    return render(request,'appnote1/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):

    products=Product.objects.all()
    return render(request,'appnote1/products.html',{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order,fields=('product','status'),extra=5)
    customer=Customer.objects.get(id=pk)
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    form=OrderForm(initial={'customer':customer})
    if request.method=='POST':
       formset=OrderFormSet(request.POST,instance=customer)
       if formset.is_valid():
           formset.save() 
           return redirect('/appnote1/')
    
      
    context={'formset':formset}

    return render(request,"appnote1/order_form.html",context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):

    order=Order.objects.get(id=pk)
    form=OrderForm(instance=order)
    if request.method=='POST':
       form=OrderForm(request.POST,instance=order)
       if form.is_valid:
           
           form.save() 
           return redirect('/appnote1/')

    context={'form':form}

    return render(request,"appnote1/update_order.html",context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method=='POST':
        order.delete()
        return redirect("/appnote1/")

    context={'item':order}

    return render(request,'appnote1/delete.html',context)

@unauthenticated_user
def registerpage(request):
        if request.user.is_authenticated:
            return redirect('/appnote1/home')
        else:

            form=CreateUserForm()
            if request.method=='POST':
            
                form=CreateUserForm(request.POST)
                if form.is_valid():
              #this allow you to place user under customer by default
                    user=form.save() 
                    username=form.cleaned_data.get('username')

                    group=Group.objects.get(name='customer')

                    user.groups.add(group)
                    Customer.objects.create(user=user,)
                    
                    messages.success(request,'account was created for ' +username)
                    return redirect('/appnote1/login')
                else:
                    form=CreateUserForm()
                    messages.success(request,'Something wentwrong')
                    context={'form':form}
                    return render(request,"appnote1/register.html",context)
            else:
                form=CreateUserForm()
                context={'form':form}
                return render(request,"appnote1/register.html",context)
        
@unauthenticated_user      
def loginpage(request):
         if request.user.is_authenticated:
            return redirect('/appnote1/home')
         else:
    
            if request.method=='POST':
                username=request.POST.get('username')
                password= request.POST.get('password')
                user=authenticate(request,username=username,password=password)

                if user is not None:
                    login(request, user)
                    return redirect('/appnote1/home')
                else:
                    messages.info(request,'Error invalid credential')
                    #mess="Error invalid credential"
                    #context={'messages':mess}
                    return render(request,"appnote1/login.html")

            else:  
                #mess="Error invalid credential"
                #context={'messages':mess}
                return render(request,"appnote1/login.html")        
            

def signout(request):
    logout(request)
    return redirect('/appnote1/login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userpage(request):
    orders=request.user.customer.order_set.all()
    
   
    total_orders=orders.count()
    
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='pending').count()

    context={'orders':orders,'delivered':delivered,'pending':pending,'total_orders':total_orders}
    return render(request,"appnote1/user.html",context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSetting(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    if request.method=='POST':
       form=CustomerForm(request.POST,request.FILES,instance=customer)
       if form.is_valid():
          form.save()
          
    context={'form':form}
    return render(request,"appnote1/account_setting.html",context)