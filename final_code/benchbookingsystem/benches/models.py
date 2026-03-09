from django.db import models
from django.conf import settings


class Bench(models.Model):

    CATEGORY_CHOICES = [
        ('IPN-10', 'iPN-10'),
        ('IPN-12', 'iPN-12'),
        ('IPN-14', 'iPN-14'),
        ('IPN-15', 'iPN-15'),
    ]

    name = models.CharField(max_length=50)
    IPN_VARIANT = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='')

    def __str__(self):
        return self.name


class TimeSlot(models.Model):

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class Booking(models.Model):

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('running', 'Running'),
        ('completed', 'Completed'),
         ("cancelled", "Cancelled"),
        ('missed', 'Missed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bench = models.ForeignKey(Bench, on_delete=models.CASCADE)
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔹 NEW FIELDS
    is_active = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('bench', 'slot', 'date')

    def __str__(self):
        return f"{self.user} - {self.bench} - {self.slot}"