from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ID = models.AutoField(primary_key=True)
    roles = (
        ('user', 'USER'),
        ('admin', 'ADMIN'),
        ('auditor', 'AUDITOR'),
        ('manager', 'MANAGER')
    )
    role = models.CharField(choices=roles,max_length=7,default='user')
    departments = (
        ('CA','Clothing and Apparel'),
        ('HD','Home and Decors'),
        ('CS','Construction Supplies')
        )
    department = models.CharField(max_length=2,choices=departments,default='CA')

    @classmethod
    def createProfile(self, data):
        exists = User.objects.filter(username=data.get("username","")).exists()
        if not exists:
            user = User(first_name=data.get("fname",""), 
                last_name=data.get("lname",""),
                username=data.get("username",""),
                email=data.get("email",""),
                is_active=True
                )
            if data.get("role","user") == 'admin':
                user.is_superuser=True
            if data.get("role","user") == 'manager':
                user.is_staff=True
            user.set_password(data.get("password",""))
            user.save()
            user.profile.role=data.get("role","user")
            user.profile.department=data.get("department","CA")
            user.save()

    #edit user, still not working, currently testing
    @classmethod
    def editUser (self, data):
        eUser=self.objects.get(pk=id)

        eUser.first_name=data.get("fname", "")
        eUser.last_name=data.get("lname", "")
        eUser.email=data.get("email", "")

        if data.get("role","user") == 'admin':
            user.is_superuser=True

        if data.get("role","user") == 'manager':
            user.is_staff=True

        eUser.profile.rold=data.get("role","")
        eUser.profile.department=data.get("department","")
        eUser.save()

        # exists = User.objects.filter(username=data.get("username","")).exists()
        # if exists:
        #     user = User(first_name=data.get("fname",""), 
        #         last_name=data.get("lname",""),
        #         email=data.get("email",""),
        #         )
        #     if data.get("role","user") == 'admin':
        #         user.is_superuser=True
        #     if data.get("role","user") == 'manager':
        #         user.is_staff=True
        #     user.save()
        #     user.profile.role=data.get("role","user")
        #     user.profile.department=data.get("department","CA")
        #     user.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Product(models.Model):
    ID = models.AutoField(primary_key=True)
    SKU = models.CharField(max_length=11,null=True)
    name = models.CharField(max_length=50,null=True)
    price = models.IntegerField(default=0)
    departments = (
        ('CA','Clothing and Apparel'),
        ('HD','Home and Decors'),
        ('CS','Construction Supplies')
        )
    department = models.CharField(max_length=2,choices=departments,default='CA')
    stocks = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)

class Inventory(models.Model):
    ID = models.AutoField(primary_key=True)
    products = models.TextField(null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING)
    status_list = (
        ('DRAFT','Draft'),
        ('REJECTED','Rejected'),
        ('TO_AUDIT','To_Audit'),
        ('TO_APPROVE','To_Approve'),
        ('APPROVED','Approved')
    )
    status = models.CharField(max_length=10,choices=status_list, default='DRAFT')
    rejects = (
        ('AUDIT', 'AUDIT'),
        ('APPROVAL','APPROVAL'),
    )
    rejected_at = models.CharField(max_length=8,choices=rejects,null=True)
    departments = (
        ('CA','Clothing and Apparel'),
        ('HD','Home and Decors'),
        ('CS','Construction Supplies')
        )
    department = models.CharField(max_length=2,choices=departments,default='CA')
    week = models.CharField(max_length=10,null=True)


    @classmethod
    def createInventory(self,user,department,data):
        products = Product.objects.filter(department=department)
        product_inventory = {}
        for product in products:
            if not str(product.ID)+'_stocks' and not str(product.ID)+'_sales' in data:
                continue
            if product.ID not in product_inventory: 
                product_inventory[product.ID] = {}
            inv_stocks = data.get(str(product.ID)+'_stocks',0)
            inv_sales = data.get(str(product.ID)+'_sales',0)
            product_inventory[product.ID]['ID'] = product.ID
            product_inventory[product.ID]['name'] = product.name
            product_inventory[product.ID]['SKU'] = product.SKU
            product_inventory[product.ID]['old_stocks'] = product.stocks
            product_inventory[product.ID]['old_sales'] = product.sales
            product_inventory[product.ID]['inv_stocks'] = inv_stocks
            product_inventory[product.ID]['inv_sales'] = inv_sales

        inventory = self(created_by=user,
                    products=json.dumps(product_inventory),
                    department=department,
                    week=data.get("week_year",""))
        if data.get("draft","") != "":
            inventory.status = 'DRAFT'
        elif data.get("to_audit","") != "":
            inventory.status = 'TO_AUDIT'
        inventory.save()

    @classmethod
    def editInventory(self,id,user,department,data):
        products = Product.objects.filter(department=department)
        product_inventory = {}
        for product in products:
            if not str(product.ID)+'_stocks' and not str(product.ID)+'_sales' in data:
                continue
            if product.ID not in product_inventory: 
                product_inventory[product.ID] = {}
            inv_stocks = data.get(str(product.ID)+'_stocks',0)
            inv_sales = data.get(str(product.ID)+'_sales',0)
            product_inventory[product.ID]['ID'] = product.ID
            product_inventory[product.ID]['name'] = product.name
            product_inventory[product.ID]['SKU'] = product.SKU
            product_inventory[product.ID]['old_stocks'] = product.stocks
            product_inventory[product.ID]['old_sales'] = product.sales
            product_inventory[product.ID]['inv_stocks'] = inv_stocks
            product_inventory[product.ID]['inv_sales'] = inv_sales
        inventory = self.objects.get(pk=id)
        inventory.products=json.dumps(product_inventory)
        inventory.week=data.get("week_year","")
        if data.get("draft","") != "":
            inventory.status = 'DRAFT'
        elif data.get("to_audit","") != "":
            inventory.status = 'TO_AUDIT'
        elif data.get("to_approve","") != "":
            inventory.status = 'TO_APPROVE'
        elif data.get("approve","") != "":
            inventory.status = 'APPROVED'
        elif data.get("reject","") != "":
            inventory.status = 'REJECTED'
        inventory.save()