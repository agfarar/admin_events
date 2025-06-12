# apps/ticket_categories/models.py

from django.db import models
from utils.models import TimeStampedModel

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre de la Empresa',blank=False, null=False)
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name

class TicketCategory(TimeStampedModel):
    ticket_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nombre")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    
    class Meta:
        verbose_name = 'Tipo de entrada'
        verbose_name_plural = 'Tipos de entradas'

    def __str__(self):
        return self.name