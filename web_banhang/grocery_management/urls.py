from django.urls import path 
from . import views

urlpatterns = [
    path('create/',views.product_create, name= "product_create"),
    path('',views.product_list, name= "product_list"), # list khoong cos path nao nen de trong bien 1
    path('update/<int:product_id>/',views.product_update, name= "product_update"),
    path('delete/<int:product_id>/',views.product_delete, name= "product_delete"),
    path('sell/<int:product_id>/',views.product_sell, name= "product_sell")
]
