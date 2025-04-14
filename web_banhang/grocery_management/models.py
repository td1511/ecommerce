from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price_purchase = models.DecimalField(max_digits=10, decimal_places=0) 
    price_selling = models.DecimalField(max_digits=10, decimal_places=0) 
    quantity = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default = 0)
    