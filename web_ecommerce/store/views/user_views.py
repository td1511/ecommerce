
from django.shortcuts import render, redirect
from store.models import User, Product  # Import model User
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.
def home(request):
    best_sellers = Product.objects.order_by('-quantity_sold')[:40]
    return render(request, 'home.html', {'best_sellers': best_sellers})


def logup_view(request):
    if request.method == "POST":
        # Lấy dữ liệu từ biểu mẫu
        name = request.POST.get("name")
        telephone = request.POST.get("telephone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Lấy thông tin vai trò

        if not telephone.isdigit() and len(telephone) != 10:
            messages.error(request, 'Số điện thoại phải là 10 chữ số!')
            return render(request, 'logup.html')
        # Kiểm tra các giá trị hợp lệ
        if not name or not email or not password or not role or not telephone:
            
            messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
            return render(request, 'logup.html')  # Khi có lỗi, trả về lại trang đăng ký
        
        # Kiểm tra xem email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            
            messages.error(request, 'Email đã tồn tại, vui lòng chọn email khác!')
            return render(request, 'logup.html')  # Khi có lỗi, trả về lại trang đăng ký

        if User.objects.filter(telephone=telephone).exists():
            
            messages.error(request, 'Telephone đã tồn tại, vui lòng chọn telephone khác!')
            return render(request, 'logup.html')  # Khi có lỗi, trả về lại trang đăng ký
        try:
            # Lưu dữ liệu vào cơ sở dữ liệu với mật khẩu được mã hóa
            user = User(
                name=name,
                telephone=telephone,
                email=email,
                password = password, 
                role=role
                #password=make_password(password),  # Mã hóa mật khẩu
            )
            user.save()

            # Nếu role là 'customer', tạo đối tượng Customer
            '''if role == 'customer':
                customer = Customer(user=user)
                customer.save()'''
            messages.success(request, 'Đăng ký thành công!')
            return redirect('login')  # dùng redirect thay vì render
  # Đăng ký thành công, chuyển đến trang home
        
        except IntegrityError:  # Xử lý lỗi email/sdt trùng lặp trong trường hợp bất ngờ
            messages.error(request, 'Thông tin đăng ký lỗi!')
            return render(request, 'logup.html')
    # Hiển thị biểu mẫu khi truy cập GET
    return render(request, 'logup.html')  # để hiển thị trang khi GET


def login_view(request):
    if request.method == "POST":
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')

        # Kiểm tra người dùng trong database
        try:
            user = User.objects.get(telephone=telephone) # lấy từ trong database ra
            if user.password == password:  # Kiểm tra mật khẩu
                #login(request, user)
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name  # Hoặc first_name tùy theo model
                request.session['role'] =user.role
                messages.success(request, 'Đăng nhập thành công!')
                return redirect('home')
                
            else:
                # Sai mật khẩu
                messages.error(request, 'Sai mật khẩu!')
                return render(request, 'login.html')
                
        except User.DoesNotExist:
            messages.error(request, 'Số điện thoại không tồn tại!')
            return render(request, 'login.html')
            
    return render(request, 'login.html')  # để hiển thị trang khi GET


def logout_view(request):
    request.session.flush()  # Xóa toàn bộ session
    messages.success(request, 'Bạn đã đăng xuất!')
    return redirect('home')


def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Thêm xử lý gửi email hoặc hiển thị thông báo ở đây nếu muốn
        messages.success(request, "Nếu email tồn tại, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu.")
        return render(request, 'password_reset.html')

    return render(request, 'password_reset.html')