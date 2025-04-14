from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import Category

def add_category_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Danh mục đã tồn tại.")
        else:
            Category.objects.create(name=name)
            messages.success(request, "Thêm danh mục thành công.")
        return redirect("add_category")  # tên URL

    categories = Category.objects.all()
    return render(request, "category.html", {"categories": categories})
