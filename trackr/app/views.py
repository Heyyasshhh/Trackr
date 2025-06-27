from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser

# Create your views here.
def index(request):
    return render(request, "index.html")

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('uname')
        email = request.POST.get('uemail')
        password = request.POST.get('upass')
        confirm_password = request.POST.get('ucpass')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'signup.html')

        # Create user instance
        newuser = CustomUser(username=name, email=email)
        newuser.set_password(password)
        newuser.is_user = True  # default to 'user' role
        newuser.save()

        messages.success(request, "Account created successfully!")
        return redirect('signin')

    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('uemail')
        password = request.POST.get('upass')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Email is not registered.")
            return redirect('signin')

        user_auth = authenticate(request, username=user.username, password=password)

        if user_auth is not None:
            login(request, user_auth)

            # Role-based redirect
            if hasattr(user_auth, 'is_user') and user_auth.is_user:
                return redirect('user_dashboard')
            elif hasattr(user_auth, 'is_dietician') and user_auth.is_dietician:
                return redirect('dietician_workspace')
            else:
                messages.warning(request, "Role not assigned.")
                return redirect('signin')
        else:
            messages.error(request, "Incorrect password.")
            return redirect('signin')

    return render(request, 'signin.html')

def userlogout(req):
    logout(req)
    return redirect("/")

def user_dashboard(request):
    return render(request, 'user_dashboard_base.html')
