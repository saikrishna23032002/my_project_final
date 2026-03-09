from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Bench, Booking



ACCESS_RULES = {
    "vendor_1": ["IPN-10", "IPN-12"],
    "vendor_2": ["IPN-12", "IPN-14"],
    "vendor_3": ["IPN-14", "IPN-15"]
}


# ---------------- SEARCH PAGE ----------------
@login_required
def bench_search(request):

    return render(request, "benches/bench_search.html")


# ---------------- AVAILABLE BENCHES ----------------
@login_required
def available_benches(request):

    date = request.GET.get("date")
    start = request.GET.get("start_time")
    end = request.GET.get("end_time")

    if not date or not start or not end:
        messages.error(request, "Please select date and time")
        return redirect("bench_search")

    start_time = datetime.strptime(start, "%H:%M").time()
    end_time = datetime.strptime(end, "%H:%M").time()

    user_role = request.user.role
    allowed_categories = ACCESS_RULES.get(user_role)

    print("user_role", user_role)
    print("allowed_categories", allowed_categories)

    # Filter benches by access rule
    if allowed_categories:
        benches = Bench.objects.filter(IPN_VARIANT__in=allowed_categories)
    else:
        benches = Bench.objects.all()

    # Get overlapping bookings
    bookings = Booking.objects.filter(
        date=date,
        slot__start_time__lt=end_time,
        slot__end_time__gt=start_time,
        bench__in=benches,
         status__in=["upcoming", "running"]

    ).exclude(status="completed").select_related("bench", "user", "slot")



    # Get booked bench ids
    booked_bench_ids = bookings.values_list("bench_id", flat=True)

    # Available benches
    available = benches.exclude(id__in=booked_bench_ids)

    # Booked bench details
    booked = []

    for booking in bookings:
        booked.append({
            "bench": booking.bench,
            "user": booking.user.username,
            "start": booking.slot.start_time,
            "end": booking.slot.end_time
        })
    time_window = (datetime.combine(datetime.today(), end_time) + timedelta(minutes=30)).time()
    upcoming_bookings = Booking.objects.filter(
        date=date,
        slot__start_time__gte=end_time,
        slot__start_time__lte=time_window,
        bench__in=benches
    ).select_related("bench", "user", "slot")

    upcoming = []
    for booking in upcoming_bookings:
        upcoming.append({
            "bench": booking.bench,
            "start": booking.slot.start_time,
            "end": booking.slot.end_time
        })

    print("upcoming",upcoming)


    return render(request, "benches/available_benches.html", {
        "benches": available,
        "booked_benches": booked,
        "date": date,
        "start": start,
        "end": end
    })

# ---------------- CONFIRM BOOKING ----------------
@login_required
def confirm_booking(request, bench_id):

    date = request.GET.get("date")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if Booking.objects.filter(
        bench_id=bench_id,
        date=date
    ).exists():

        messages.error(request, "Bench already booked")
        return redirect("bench_search")

    Booking.objects.create(
        user=request.user,
        bench_id=bench_id,
        date=date
    )

    messages.success(request, "Booking Confirmed")

    return redirect("bench_search")

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime

from .models import Booking, TimeSlot



@login_required
def book_ticket(request, bench_id):

    date = request.GET.get("date")
    start = request.GET.get("start")
    end = request.GET.get("end")

    print(date, start, end)

    # convert string to time
    start_time = datetime.strptime(start, "%H:%M").time()
    end_time = datetime.strptime(end, "%H:%M").time()

    # get or create slot
    slot, created = TimeSlot.objects.get_or_create(
        start_time=start_time,
        end_time=end_time
    )

    # check if already booked
    exists = Booking.objects.filter(
        bench_id=bench_id,
        slot=slot,
        date=date
    ).exists()

    if exists:
        messages.error(request, "Bench already booked for this slot")
        return redirect("bench_search")

    # create booking
    Booking.objects.create(
        user=request.user,
        bench_id=bench_id,
        slot=slot,
        date=date
    )

    messages.success(request, "Booking Confirmed Successfully")

    return redirect("my_bookings")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Bench, Booking

ACCESS_RULES = {
    "vendor_1": ["IPN-10", "IPN-12"],
    "vendor_2": ["IPN-12", "IPN-14"],
    "vendor_3": ["IPN-14", "IPN-15"]
}

def display_bench_list(request):
    selected_ipn = request.GET.get("ipn", "")

    if request.user.role == "manager":
        benches = Bench.objects.all()
    else:
        allowed_ipn = ACCESS_RULES.get(request.user.role, [])
        benches = Bench.objects.filter(IPN_VARIANT__in=allowed_ipn)

    # Apply IPN Variant filter
    if selected_ipn:
        benches = benches.filter(IPN_VARIANT=selected_ipn)

    # Prepare bench data
    bench_data = []
    for bench in benches:
        last_booking = Booking.objects.filter(
            bench=bench,
            status="completed"
        ).order_by("-last_activity").first()

        bench_data.append({
            "bench": bench,
            "last_user": last_booking.user.username if last_booking else "-",
            "last_exit": last_booking.last_activity if last_booking else "-"
        })

    return render(request, "benches/display_bench_list.html", {
        "bench_data": bench_data,
        "ipn_choices": Bench.CATEGORY_CHOICES,
        "selected_ipn": selected_ipn
    })




@login_required
def booked_benches(request):
    # Filter only upcoming bookings
    if request.user.role == "manager":
        bookings = Booking.objects.filter(status="upcoming") \
            .select_related("bench", "user", "slot") \
            .order_by("date", "slot__start_time")
    else:
        # Vendors see only their own role benches
        from .models import Bench
        # Get allowed IPN_VARIANTs for this vendor
        ACCESS_RULES = {
            "vendor_1": ["IPN-10", "IPN-12"],
            "vendor_2": ["IPN-12", "IPN-14"],
            "vendor_3": ["IPN-14", "IPN-15"]
        }
        allowed_variants = ACCESS_RULES.get(request.user.role, [])
        bookings = Booking.objects.filter(
            status="upcoming",
            bench__IPN_VARIANT__in=allowed_variants
        ).select_related("bench", "user", "slot").order_by("date", "slot__start_time")

    return render(request, "booked_benches.html", {
        "bookings": bookings
    })

from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def recently_booked_benches(request):
    """
    Shows benches with recent bookings including actual slot start/end if slot started.
    Manager sees all benches; vendor sees only benches for their IPN_VARIANT.
    Automatically updates status to 'completed' if slot ended.
    """
    now = timezone.localtime()

    if request.user.role == "manager":
        recent_bookings = Booking.objects.select_related("bench", "user", "slot") \
            .order_by("-date", "-slot__start_time")[:5]
    else:
        allowed_ipn = ACCESS_RULES.get(request.user.role, [])
        recent_bookings = Booking.objects.select_related("bench", "user", "slot") \
            .filter(bench__IPN_VARIANT__in=allowed_ipn) \
            .order_by("-date", "-slot__start_time")[:5]

    recently_booked = []
    for booking in recent_bookings:
        slot_start_datetime = timezone.make_aware(
            datetime.combine(booking.date, booking.slot.start_time)
        )
        slot_end_datetime = timezone.make_aware(
            datetime.combine(booking.date, booking.slot.end_time)
        )

        # ✅ Automatically update status if slot ended
        if now >= slot_end_datetime and booking.status not in ["completed", "cancelled"]:
            booking.status = "completed"
            booking.save()

        if now >= slot_start_datetime:  # Slot has started
            actual_start = booking.last_activity if booking.last_activity else "N/A"
            actual_end = slot_end_datetime if booking.status == "completed" else "Running"
            status = "Slot Started" if booking.status == "running" else booking.status.capitalize()
        else:
            actual_start = "-"
            actual_end = "-"
            status = booking.status.capitalize()

        recently_booked.append({
            "bench": booking.bench,
            "last_user": booking.user.username,
            "last_booking_date": booking.date,
            "slot_start": booking.slot.start_time,
            "slot_end": booking.slot.end_time,
            "actual_start": actual_start,
            "actual_end": actual_end,
            "status": status
        })

    return render(request, "benches/recently_booked_benches.html", {
        "recently_booked": recently_booked
    })