from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from accounts.managers import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(blank=True, null=True, max_length=100,
                                validators=[UnicodeUsernameValidator()])
    email = models.EmailField(_('email address'), unique=True)
    balance = models.FloatField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email