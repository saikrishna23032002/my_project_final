from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from benches.models import Booking


@shared_task
def release_inactive_benches():

    limit = timezone.now() - timedelta(minutes=5)

    inactive_bookings = Booking.objects.filter(
        is_active=True,
        last_activity__lt=limit
    )

    for booking in inactive_bookings:

        booking.status = "completed"
        booking.is_active = False
        booking.save()