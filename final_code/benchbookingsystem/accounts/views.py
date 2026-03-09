from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.shortcuts import get_object_or_404
from benches.models import Booking



# ---------------- LOGIN ----------------
def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("home")
        else:
            messages.error(request, "Invalid Email or Password")

    return render(request, "login.html")


# ---------------- SIGNUP ----------------
def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # Username validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        # Email validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "signup.html")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")


# ---------------- HOME ----------------
@login_required
def home(request):
    return render(request, "home.html")


# ---------------- VENDOR DASHBOARDS ----------------
@login_required
def vendor_1(request):
    return render(request, "vendor_1.html")


@login_required
def vendor_2(request):
    return render(request, "vendor_2.html")


@login_required
def vendor_3(request):
    return render(request, "vendor_3.html")


# ---------------- MANAGER DASHBOARD ----------------
@login_required
def manager(request):

    if request.user.role != "manager":
        messages.error(request, "Access denied")
        return redirect("home")
    missed_bookings = Booking.objects.filter(status="missed")
    cancelled_bookings = Booking.objects.filter(status="cancelled")

    return render(request, "manager.html", {
        "missed_bookings": missed_bookings,
        "cancelled_bookings": cancelled_bookings
    })
    



# ---------------- USERS LIST ----------------
@login_required
def users_list(request):

    if request.user.role != "manager":
        messages.error(request, "Access denied")
        return redirect("home")

    users = User.objects.filter(is_superuser=False)

    return render(request, "users_list.html", {"users": users})





# CREATE USER (Manager Only)
@login_required
def create_user(request):

    if request.user.role != "manager":
        messages.error(request, "Access denied")
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("create_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("create_user")

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        messages.success(request, "User created successfully")
        return redirect("users_list")

    return render(request, "create_user.html")


# DELETE USER (Manager Only)
@login_required
def delete_user(request, user_id):

    if request.user.role != "manager":
        messages.error(request, "Access denied")
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    # Prevent manager deleting himself
    if user == request.user:
        messages.warning(request, "You cannot delete your own account")
        return redirect("users_list")

    user.delete()

    messages.success(request, "User deleted successfully")

    return redirect("users_list")

    if request.user.role != "manager":
        messages.error(request, "Access denied")
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    user.delete()

    messages.success(request, "User deleted successfully")

    return redirect("users_list")


@login_required
def vendor_users(request):

    # Vendors only see their own role users
    if request.user.role != "manager":
        users = User.objects.filter(role=request.user.role, is_superuser=False)

    else:
        # Manager can filter by role
        filter_role = request.GET.get("role")
        if filter_role and filter_role != "all":
            users = User.objects.filter(role=filter_role, is_superuser=False)
        else:
            users = User.objects.filter(is_superuser=False)

    # Pass list of vendor roles for dropdown
    vendor_roles = [r[0] for r in User.ROLE_CHOICES if r[0] != "manager"]

    return render(request, "vendor_users.html", {
        "users": users,
        "vendor_roles": vendor_roles,
        "selected_role": request.GET.get("role", "all")
    })