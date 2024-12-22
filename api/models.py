from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Ticket(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.title


class AppVersion(models.Model):
    version_number = models.CharField(max_length=50)
    file = models.FileField(upload_to='app_versions/')
    additional_file = models.FileField(upload_to='app_versions/', null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Version {self.version_number}"



class Bug(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bugs')
    hardwareCode = models.CharField(max_length=100, unique=False)
    softwareCode = models.CharField(max_length=100, unique=False)
    bugTxt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Bug {self.id} by {self.user.username}"


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='logs', on_delete=models.CASCADE)
    hardwareCode = models.CharField(max_length=100, unique=True)
    softwareCode = models.CharField(max_length=100, unique=True)
    logTxt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.hardwareCode} - {self.logTxt}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True , null=True)  
    phone_number = models.CharField(max_length=15, unique=False, blank=True , null=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'serial_number', 'phone_number'] 
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

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL) 
post_save.connect(save_user_profile, sender=settings.AUTH_USER_MODEL)  


class Examination(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='examinations')
    dataset = models.CharField(max_length=200)  
    design_title = models.CharField(max_length=200)
    last_uid = models.CharField(max_length=50)
    high_heel = models.BooleanField(default=False)
    has_shoe = models.BooleanField(default=False)
    single_foot = models.BooleanField(default=False)
    download = models.FileField(upload_to='downloads/')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.design_title