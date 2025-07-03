from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, UserProfile
from django.contrib.auth.decorators import login_required
import random

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

            # ✅ Redirect based on whether UserProfile exists
            if hasattr(user_auth, 'userprofile'):
                return redirect('user_dashboard')
            else:
                return redirect('userdata')  # First-time users fill this

        else:
            messages.error(request, "Incorrect password.")
            return redirect('signin')

    return render(request, 'signin.html')

def userlogout(req):
    logout(req)
    return redirect("/")


from datetime import date
from .models import HealthLog, UserProfile

@login_required
def user_dashboard(request):
    user = request.user
    profile = UserProfile.objects.filter(user=user).first()

    # Fetch today's health log if it exists
    today_log = HealthLog.objects.filter(user=user, date=date.today()).first()

    # Select wellness tip of the day (static and rotated by date)
    tips = [
        "Stay hydrated 💧—aim for 8 glasses of water daily.",
        "Take a 5-minute stretch break every hour 🧘.",
        "Get at least 7–8 hours of sleep 😴.",
        "Eat a rainbow of fruits and vegetables 🌈🥗.",
        "Start your day with a brisk walk 🚶‍♂️☀️.",
        "Practice deep breathing for 2 minutes 🫁.",
    ]

    import hashlib
    hash_val = int(hashlib.sha256(str(date.today()).encode()).hexdigest(), 16)
    index = hash_val % len(tips)
    daily_tip = tips[index]

    return render(request, 'user_dashboard_base.html', {
        'profile': profile,
        'random_tip': daily_tip,
        'today_log': today_log,
    })


from .models import UserProfile
@login_required
def userdata(request):
    user = request.user

    # If already filled
    if hasattr(user, 'userprofile'):
        return redirect('user_dashboard')

    if request.method == 'POST':
        if request.POST.get('skip') == 'true':
            # Save only minimal profile with default/blank values
            UserProfile.objects.create(
                user=user,
                gender='Other',  # default value or blank
                mobile=9999999999  # dummy but valid format (10-digit)
            )
            return redirect('user_dashboard')

        data = request.POST
        photo = request.FILES.get('photo')

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'mobile', 'gender']
        for field in required_fields:
            if not data.get(field):
                return render(request, 'userdata.html', {
                    'error': f"{field.replace('_', ' ').capitalize()} is required.",
                    'user_email': user.email
                })

        # Save base user info
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.save()

        # Extract and process weight info
        try:
            weight = float(data.get('weight')) if data.get('weight') else 0
            target_weight = float(data.get('target_weight')) if data.get('target_weight') else 0
        except ValueError:
            weight = target_weight = 0

        # Determine goal if not provided
        goal = data.get('goal') or None
        if not goal and weight and target_weight:
            if target_weight > weight:
                goal = 'Gain Muscle'
            elif target_weight < weight:
                goal = 'Lose Weight'
            else:
                goal = 'Maintain Weight'

        # Save profile info
        UserProfile.objects.create(
            user=user,
            mobile=data.get('mobile'),
            gender=data.get('gender'),
            height=data.get('height') or None,
            weight=data.get('weight') or None,
            dietary_preference=data.get('dietary_preference') or None,
            activity_level=data.get('activity_level') or None,
            target_weight=data.get('target_weight') or None,
            goal=goal,
            photo=photo,
            medical_conditions=data.get('medical_conditions') or "",
            allergies=data.get('allergies') or "",
            medications=data.get('medications') or "",
        )

        return redirect('user_dashboard')

    return render(request, 'userdata.html', {'user_email': user.email})

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('userdata')
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        profile.mobile = request.POST.get('mobile')
        profile.gender = request.POST.get('gender')
        if request.FILES.get('photo'):
            profile.photo = request.FILES.get('photo')
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_dashboard')
    return HttpResponseNotAllowed(['POST'])

@login_required
def edit_personal_stats(request):
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        profile.height = request.POST.get('height') or None
        profile.weight = request.POST.get('weight') or None
        profile.target_weight = request.POST.get('target_weight') or None
        profile.save()

        messages.success(request, "Personal stats updated successfully!")
        return redirect('user_dashboard')

    return HttpResponseNotAllowed(['POST'])

def aboutUs(request):
    return render(request, 'aboutUs.html')

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def contactUs(request):
    success = False

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        subject = f"New Contact Message from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        success = True

    return render(request, "contactUs.html", {"success": success})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import CustomUser 


def request_password(req):
    if req.method == "POST":
        uemail = req.POST.get("uemail")
        print(uemail)
        try:
            chkemail = CustomUser.objects.get(email=uemail)
            print(chkemail)  # username

            userotp = random.randint(1111, 9999)
            req.session["otp"] = userotp

            subject = "Bookify- OTP for Reset Password"
            msg = f"Hello {chkemail}\n Your OTP to rest password is:{userotp}\n Thank you for using our services."
            emailfrom = settings.EMAIL_HOST_USER
            receiver = [chkemail.email]
            send_mail(subject, msg, emailfrom, receiver)

            return redirect("reset_password", uemail=chkemail.email)
        except CustomUser.DoesNotExist:
            messages.error(req, "No account found with this email id")
            return render(req, "request_password.html")
    else:
        return render(req, "request_password.html")


def reset_password(req, uemail):
    user = CustomUser.objects.get(email=uemail)
    print(user)
    if req.method == "POST":
        otp_entered = req.POST.get("otp")
        upass = req.POST.get("upass")
        ucpass = req.POST.get("ucpass")
        otp_saved = req.session.get("otp")
        print(otp_entered, type(otp_entered))
        print(otp_saved, type(otp_saved))

        print(upass, ucpass)
        if int(otp_entered) != int(otp_saved):
            messages.error(req, "OTP does not matched! Try Again")
            return render(req, "reset_password.html", {"uemail": uemail})

        elif upass != ucpass:
            messages.error(
                req, "New Password and confirm password does not match. Try again"
            )
            return render(req, "reset_password.html", {"uemail": uemail})
        else:
            user.set_password(upass)
            user.save()
            messages.success(req, "Password reset done successfully!")
            return redirect("signin")
    else:
        return render(req, "reset_password.html", {"uemail": uemail})

from django.contrib.auth import update_session_auth_hash
@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('change_password')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, "Your password was updated successfully!")
        return redirect('dashboard')  

    return render(request, "change_password.html")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile

@login_required
def bmi_calculator(request):
    bmi = None
    category = ""
    message = ""
    height = None
    weight = None

    try:
        # Get the logged-in user's profile
        profile = UserProfile.objects.get(user=request.user)
        height = profile.height  # in cm
        weight = profile.weight  # in kg

        # Only calculate BMI if both height and weight are available
        if height and weight:
            height_m = height / 100  # Convert to meters
            bmi = round(weight / (height_m ** 2), 1)

            # Determine BMI category and message
            if bmi < 18.5:
                category = "Underweight"
                message = "🟡 Your BMI is in the underweight range. Consider consulting a nutritionist."
            elif 18.5 <= bmi <= 24.9:
                category = "Healthy Weight"
                message = "🟢 Great! Your BMI is within the healthy range. Keep up the good work!"
            elif 25.0 <= bmi <= 29.9:
                category = "Overweight"
                message = "🟠 Your BMI suggests you're overweight. Consider exercise and a balanced diet."
            else:
                category = "Obese"
                message = "🔴 Your BMI is in the obese range. Please consult a healthcare professional."
        else:
            message = "⚠️ Please complete your profile with height and weight to calculate BMI."

    except UserProfile.DoesNotExist:
        message = "⚠️ User profile not found. Please create or update your profile first."

    context = {
        "bmi": bmi,
        "category": category,
        "message": message,
        "height": height,
        "weight": weight,
    }

    return render(request, "bmi_calculator.html", context)

from .models import HealthLog
@login_required
def health_stats(request):
    if request.method == "POST":
        calories = request.POST.get("calories")
        water = request.POST.get("water")
        steps = request.POST.get("steps")
        sleep = request.POST.get("sleep")

        # You can also get height/weight from user profile if needed
        profile = request.user.userprofile

        HealthLog.objects.create(
            user=request.user,
            weight=profile.weight or 0,
            height=profile.height or 0,
            water_intake=water,
            calories=calories,
            sleep_hours=sleep,
            steps=steps
        )

        return redirect("user_dashboard")  # redirect to dashboard or any success page

    return render(request, "health_stats.html")

@login_required
def set_daily_target(request):
    if request.method == 'POST':
        user = request.user
        user.daily_calories = request.POST.get('daily_calories')
        user.daily_water = request.POST.get('daily_water')
        user.daily_steps = request.POST.get('daily_steps')
        user.save()
        messages.success(request, "Daily targets updated successfully.")
        return redirect('user_dashboard')

