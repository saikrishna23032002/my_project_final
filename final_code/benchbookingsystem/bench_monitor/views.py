from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

from benches.models import Booking
from datetime import datetime, timedelta


@login_required
def my_bookings(request):

    bookings = Booking.objects.filter(user=request.user)

    return render(request, "bench_monitor/my_bookings.html", {
        "bookings": bookings
    })


@login_required
def connect_bench(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    now = timezone.localtime()
    start = booking.slot.start_time
    end = booking.slot.end_time

    slot_start = datetime.combine(booking.date, start)
    slot_end = datetime.combine(booking.date, end)

    slot_start = timezone.make_aware(slot_start)
    slot_end = timezone.make_aware(slot_end)

    grace_limit = slot_start + timedelta(minutes=5)

    # BEFORE SLOT
    if now < slot_start:
        messages.warning(request, "You can access the bench only during your slot time.")
        return redirect('my_bookings')
    
    if now > grace_limit and booking.status == "upcoming":
        booking.status = "missed"
        booking.save()

        messages.error(request, "You missed your slot (5 minute limit exceeded).")
        return redirect("my_bookings")

    # AFTER SLOT
    if now > slot_end:
        booking.status = "completed"
        booking.save()

        messages.error(request, "Your slot time has already finished.")
        return redirect('my_bookings')

    # DURING SLOT
    booking.status = "running"
    booking.last_activity = timezone.now()
    booking.save()

    messages.success(request, "Bench connected successfully.")

    return redirect('monitor_page', booking_id=booking.id)


@login_required
def heartbeat(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    booking.last_activity = timezone.now()
    booking.save()

    return JsonResponse({"status": "alive"})



@login_required
def monitor_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    now = timezone.localtime()

    slot_start_datetime = timezone.make_aware(
        datetime.combine(booking.date, booking.slot.start_time)
    )
    slot_end_datetime = timezone.make_aware(
        datetime.combine(booking.date, booking.slot.end_time)
    )

    # check wrong date
    if now.date() != booking.date:
        messages.error(request, "You can access the bench only on the booked date.")
        return redirect("my_bookings")

    # check before slot
    if now < slot_start_datetime:
        messages.warning(request, "You can access the bench only during your slot time.")
        return redirect("my_bookings")

    # check inactivity
    if booking.last_activity and (now - booking.last_activity) > timedelta(minutes=1):
        booking.status = "completed"
        booking.save()
        messages.error(
            request,
            f"Session for user '{booking.user.username}' on bench '{booking.bench.name}' expired due to inactivity."
        )
        return redirect("my_bookings")

    # after slot ended
    if now > slot_end_datetime and booking.status != "completed":
        booking.status = "completed"
        booking.save()
        messages.info(request, "Your slot time has finished.")
        return redirect("my_bookings")

    # if slot has started, mark it running
    if slot_start_datetime <= now <= slot_end_datetime and booking.status == "upcoming":
        booking.status = "running"
        booking.last_activity = now
        booking.save()

    return render(request, "bench_monitor/monitor.html", {
        "booking": booking,
        "slot_start": slot_start_datetime,
        "slot_end": slot_end_datetime,
        "now": now
    })
@login_required
def disconnect_bench(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    booking.status = "completed"
    booking.save()

    messages.success(request, "Bench session ended successfully.")

    return redirect("my_bookings")



from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def cancel_booking(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    now = timezone.localtime()

    slot_start = datetime.combine(booking.date, booking.slot.start_time)
    slot_start = timezone.make_aware(slot_start)

    # allow cancel only before slot start
    if now >= slot_start:
        messages.error(request, "You cannot cancel after the slot has started.")
        return redirect("my_bookings")

    booking.status = "cancelled"
    booking.save()

    messages.success(request, "Booking cancelled successfully.")

    return redirect("my_bookings")