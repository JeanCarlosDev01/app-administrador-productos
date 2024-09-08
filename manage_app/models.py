from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField()
    price = models.IntegerField()
    create_date = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Description(models.Model):
    description = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
class ProductImages(models.Model):
    url = models.URLField(max_length=500)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)