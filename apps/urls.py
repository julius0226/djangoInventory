from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('users/', views.users, name='users'),	
    path('users/add', views.add_user, name='addUser'),
    path('users/delete/<id>', views.delete_user, name='deleteUser'),
    path('users/edit/<id>', views.edit_user, name='editUser'),
    path('inventory/', views.inventory, name='inventory'),
	path('inventory/add', views.add_inventory, name='addInventory'),
	path('inventory/delete/<id>', views.delete_inventory, name='deleteInventory'),
	path('inventory/edit/<id>', views.edit_inventory, name='editInventory'),
]
