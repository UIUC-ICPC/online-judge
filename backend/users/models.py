from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

class CustomUser(AbstractBaseUser, PermissionsMixin):
  username = models.CharField(max_length=255, unique=True) 
  email = models.EmailField(verbose_name="email address", unique=True)
  date_joined = models.DateTimeField(default=timezone.now)
  is_staff = models.BooleanField(default=False) 
  is_active = models.BooleanField(default=True) 
  
  USERNAME_FIELD = "username"
  REQUIRED_FIELDS = ["email"]

  objects = UserManager()
  
  def __str__(self):
    return self.username
  
  
  
  
