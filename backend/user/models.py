import datetime

from django.db import models


#signals import
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


# Custom User Manager:

class MyUserManager(BaseUserManager):
    def create_user(self, email, name,is_staff, password=None, password2=None):
        """
        Create and Save User with email name,tc, password
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_staff=is_staff
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            is_staff=True
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Custom User Model

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin and self.is_staff

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

# @receiver(pre_save,sender=User)
# def print_anything(sender,instance,**kwargs):
#     print(instance.is_staff) #this gives the post save value
#     print(sender.objects.get(id=instance.id).is_staff) #this provide the pre save value from the model direct.


class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    img = models.URLField(null=True)
    age = models.IntegerField(default=18)
    phone = models.CharField(null=True, max_length=20, default=None)
    Male = 'M'
    Female = 'F'
    Others = 'O'
    GENDER_CHOICES = [
        (Male, 'Male'),
        (Female, 'Female'),
        (Others, 'Others'),
    ]
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        default=Male,
    )
    details_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    img = models.URLField(null=True)
    phone = models.CharField(null=True, max_length=20,default=None)
    qualification = models.CharField(max_length=200, default=None)
    speciality = models.CharField(max_length=200, default=None)
    hosp_name = models.CharField(max_length=200, default=None)
    experience = models.PositiveIntegerField(default=0)
    fees = models.PositiveIntegerField(default=399)
    slot_start = models.DateTimeField(default=None)
    slot_end = models.DateTimeField(default=None)
    age = models.IntegerField(default=18)
    Male = 'M'
    Female = 'F'
    Others = 'O'
    GENDER_CHOICES = [
        (Male, 'Male'),
        (Female, 'Female'),
        (Others, 'Others'),
    ]
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        default=Male,
    )
    available = models.BooleanField(default=True)
    details_status = models.BooleanField(default=False)
    admin_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name
