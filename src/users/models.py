import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, is_admin=False):
        if not email:
            raise ValueError("Users must provide a valid email address.")
        if not username:
            raise ValueError("Users must provide a unique username.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_admin=is_admin,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        return self.create_user(username=username, email=email, password=password, is_admin=True)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=128)
    
    is_admin = models.BooleanField(default=False)
    
    refresh_token = models.TextField(blank=True, null=True)
    refresh_expiration_date = models.DateTimeField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password):
        self.password_hash = self.set_password(raw_password)

    def __str__(self):
        return self.username