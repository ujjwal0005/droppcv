from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework.parsers import MultiPartParser, FormParser

class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        return self.create_user(email, password, **other_fields)

class User(AbstractBaseUser, PermissionsMixin):
    parser_classes = (MultiPartParser, FormParser)

    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profile/',null=True,blank =True)
    user_type = models.CharField(max_length=255,choices=(('employee','Employee'),('employer','Employer'),('other','Other')))

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'  # Required for Django authentication
    REQUIRED_FIELDS = ['name', 'user_type']

    def __str__(self):
        return self.email

class EmployeeProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', primary_key=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    location = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    service_type = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True)
    work_experience = models.CharField(max_length=255, null=True, blank=True)
    salary_expectation = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f'{self.user.email} - Employee'

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile', primary_key=True)
    company_name = models.CharField(max_length=255)
    cuurent_position = models.CharField(max_length=255)
    qualification_certificate = models.FileField(upload_to='files/',null=True,blank=True)
    work_experience = models.CharField(max_length=255,null=True,blank=True)
    location = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.user.email} - Employer'

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name