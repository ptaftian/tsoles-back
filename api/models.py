from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Bug(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bugs')
    hardwareCode = models.CharField(max_length=100)
    softwareCode = models.CharField(max_length=100)
    bugTxt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bug {self.id} by {self.user.username}"

class AppVersion(models.Model):
    version_number = models.CharField(max_length=50)  # e.g., "1.0.0"
    file = models.FileField(upload_to='app_versions/')  # File field for the new version
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the version was created

    def __str__(self):
        return f"Version {self.version_number}"


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='logs', on_delete=models.CASCADE)  # Use AUTH_USER_MODEL here
    hardwareCode = models.CharField(max_length=100)
    softwareCode = models.CharField(max_length=100)
    logTxt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hardwareCode} - {self.logTxt}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True)  # Add serial number field
    phone_number = models.CharField(max_length=15, unique=True, blank=True)  # Add phone number field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'serial_number', 'phone_number']  # Add new fields to required fields

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    bio = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user_images", default="default.jpg")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)  # Changed to AUTH_USER_MODEL
post_save.connect(save_user_profile, sender=settings.AUTH_USER_MODEL)  # Changed to AUTH_USER_MODEL