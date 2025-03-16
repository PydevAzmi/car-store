import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django_countries.fields import CountryField

GENDER = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ("Prefer not to say", "Prefer not to say"),
]


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150)
    phone_number = models.CharField(
        _("Phone Number"), max_length=14, null=True, blank=True
    )
    gender = models.CharField(
        _("Gender"), max_length=50, choices=GENDER, null=True, blank=True
    )
    location = models.ForeignKey(
        'Location', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_trader = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.username


class TraderProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='trader_profile'
    )
    company_name = models.CharField(max_length=255, blank=True)
    VAT_number = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.0
    )  # Default commission %
    payment_details = models.TextField(blank=True)
    approved = models.BooleanField(default=False)  # Admin approval status
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    response_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        verbose_name=_("user"),
        related_name="user_profile",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_trader:
            TraderProfile.objects.create(user=instance)
        Profile.objects.create(user=instance)


class Location(models.Model):
    country = CountryField()
    city = models.CharField(_("city"), max_length=50)
    state = models.CharField(_("state"), max_length=50)
    street = models.CharField(_("street"), max_length=50)

    def __str__(self):
        return f'{(self.city)[:10]}, {(self.state)[:10]}, {(self.street)[:10]}...'
