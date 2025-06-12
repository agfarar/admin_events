# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.ticket_categories.models import Company  # Importa el modelo de Company desde tu aplicación principal

class CustomUser(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False, related_name='users')

    def __str__(self):
        return self.username
