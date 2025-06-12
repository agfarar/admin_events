# apps/inventory/models.py
from django.db import models
from simple_history.models import HistoricalRecords
from apps.events.models import Event
from accounts.models import CustomUser
from django import forms

class InventoryItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='inventory_items', verbose_name='Evento', help_text='Evento al que pertenece el item')
    name = models.CharField(max_length=255, verbose_name='Nombre', help_text='Nombre del producto o item como sillas')
    add_stock = models.IntegerField(default=0, verbose_name='Añadir stock o quitar', help_text='Cambia el numero para añadir o quitar stock ejemplo -1 quita y 1 del stock')
    quantity_available = models.PositiveIntegerField(default=0, verbose_name='Cantidad Disponible', help_text='Cantidad disponible en stock')
    quantity_sold = models.PositiveIntegerField(default=0, verbose_name='Cantidad Vendida', help_text='Cantidad vendida')
    category = models.CharField(max_length=255, blank=True, null=True, verbose_name='Categoría', help_text='Productos / Alimentos / Decoración / Sonido')
    price = models.PositiveIntegerField(default=0, verbose_name='Precio base', help_text='Precio del item')
    price_category_sold = models.PositiveIntegerField(default=0, verbose_name='Precio de Venta', help_text='Precio de venta del item')
    is_category_sold = models.BooleanField(default=False, verbose_name='¿Se venderá?', help_text='Si el item se venderá o no')
    created_by = models.ForeignKey(CustomUser, related_name='inventory_items_created', on_delete=models.SET_NULL, null=True, editable=False, verbose_name='Creado por', help_text='Usuario que creó el item')
    updated_by = models.ForeignKey(CustomUser, related_name='inventory_items_updated', on_delete=models.SET_NULL, null=True, editable=False, verbose_name='Actualizado por', help_text='Usuario que actualizó el item')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Inventario de Evento'
        verbose_name_plural = 'Inventarios de Eventos'
        unique_together = ('event', 'name')

    def __str__(self):
        return f"{self.name} ({self.quantity_available} en stock)"

    def update_stock(self, quantity):
        self.quantity_available += quantity
        self.save()

    def update_quantity_sold(self, quantity):
        self.quantity_sold += quantity
        self.save()

    def use_stock(self, quantity):
        if quantity <= self.quantity_available:
            self.quantity_available -= quantity
            self.save()
        else:
            raise ValueError("No hay suficiente stock disponible")

    def save(self,expenses_save=False, *args, **kwargs):
        # # validamos el campo add_stock si es negativo reste a quantity_available
        # if self.add_stock < 0 and self.quantity_available < abs(self.add_stock):
        #     # mostramos error en el campo de add_stock si no hay suficiente stock disponible
        #     raise forms.add_stock.ValidationError("No hay suficiente stock disponible")
        
        if not expenses_save:
            if self.add_stock > 0:
                self.quantity_available += self.add_stock
            else: 
                self.quantity_available -= abs(self.add_stock)
        
            # reseteamos add_stock despues de sumar a quantity_available
            self.add_stock = 0

            # llama al metodo save de la clase padre para guardar el objeto
        super().save(*args, **kwargs)

    # Capturamos el error que se genera en save para mostrarlo en el campo del formulario
    # def clean(self):
    #     try:
    #         self.save()
    #     except ValueError as e:
    #         raise forms.ValidationError("No hay suficiente stock disponible")