from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('vendor_1', 'Vendor_1'),
        ('vendor_2', 'Vendor_2'),
        ('vendor_3', 'Vendor_3'),
        ('manager', 'Manager'),
    )
    SUB_ROLE_CHOICES = (
        ('user', 'User'),
        ('manager', 'Manager'),
    )

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    sub_role = models.CharField(
        max_length=10,
        choices=SUB_ROLE_CHOICES,
        default='user',     # prevents migration errors
        blank=True
    )

