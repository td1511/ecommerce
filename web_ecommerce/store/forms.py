from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'price_purchase','price_selling', 'quantity_sold', 
            'quantity_left',  'discount','brand'
        ]
        

    
