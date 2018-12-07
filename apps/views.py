from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from .models import Profile, Product, Inventory
import json


def home(request):
    return render(request,'authenticate/home.html', {})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user) 
            messages.success(request, ("Login successfull, welcome " + user.username + '!' ))
            return redirect('home')
        else:
            messages.success(request, ('Wrong credentials, please try again.'))
            return redirect('login')
    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('Logout successfull!'))
    return redirect('home')

user_auditor = user_passes_test(lambda user: user.profile.role == 'auditor')
def is_auditor(view_func):
    decorated_view_func = login_required(user_auditor(view_func))
    return decorated_view_func

user_personnel = user_passes_test(lambda user: user.profile.role == 'user')
def is_personnel(view_func):
    decorated_view_func = login_required(user_personnel(view_func))
    return decorated_view_func	

user_admin = user_passes_test(lambda user: user.is_superuser )
def is_admin(view_func):
    decorated_view_func = login_required(user_admin(view_func))
    return decorated_view_func

@is_admin
def add_user(request):
    if request.method == 'GET':
        return render(request, 'authenticate/adduser.html')
    elif request.method == 'POST':
        Profile.createProfile(request.POST) 
        messages.success(request, ('New user added.'))       
    return redirect ('home')

@login_required
def users(request):
	users = User.objects.all()

	context = {
		'users':users
	}
	return render(request,'authenticate/users.html',context)  



@is_admin
@login_required
def delete_user(request, id):
    if request.method == 'POST': 
        deleteUser = User.objects.get(pk=id)
        deleteUser.delete()
        messages.success(request, ('Selected user deleted.')) 
    return redirect('users')

##working on edit
@is_admin
@login_required
def edit_user(request, id):
	if request.method == 'GET': 
		users = User.objects.get(pk=id)
		context = {
			'users':users
		}
		return render(request,'authenticate/edituser.html',context)  
	elif request.method == 'POST':
		Profile.editUser(request.POST) 
		messages.success(request, ('User updated.'))   
		return HttpResponseRedirect("/authenticate/users")

	

##Inventory
@login_required
def inventory(request):
	inventories = Inventory.objects.all()

	context = {
		'inventories':inventories
	}
	return render(request,'authenticate/inventory.html',context)

@login_required
def delete_inventory(request,id):
	if request.method == 'POST':
		inventory = Inventory.objects.get(pk=id)
		inventory.delete()
		return redirect('inventory')

def edit_inventory(request,id):

	user = request.user
	department =user.profile.department
	if request.method == 'GET':
		inventory = Inventory.objects.get(pk=id)
		products_json = json.loads(inventory.products)
		products = [products_json[key] for key in products_json]
		departments = {
			"CA": "Clothing and Apparel",
			"HD": "Home and Decors",
			"CS": "Construction Supplies"
		}
		context = {
			'inventory': inventory,
			'products': products,
			'user': user
		}
		return render(request, 'authenticate/editinventory.html',context)
	elif request.method == 'POST':
		Inventory.editInventory(id,user,department,request.POST)
		return HttpResponseRedirect("/authenticate/inventory")

#get departments from db
def add_inventory(request):
	user = request.user
	department =user.profile.department
	# departments = Profile.department.objects.all()
	if request.method == 'GET':
		products = Product.objects.filter(department=department)
		context = {
			'products':products
			# 'departments':departments
		}
		return render(request, 'authenticate/addinventory.html',context)
	elif request.method == 'POST':
		Inventory.createInventory(user,department,request.POST)
		return HttpResponseRedirect("/authenticate/inventory")    


