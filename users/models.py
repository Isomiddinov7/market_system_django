from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("The email field must be set")
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
