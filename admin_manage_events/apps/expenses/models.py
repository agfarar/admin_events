# apps/expenses/models.py
from django.db import models
from apps.events.models import Event
from apps.ticket_categories.models import Company
from apps.inventory.models import InventoryItem
from accounts.models import CustomUser
from simple_history.models import HistoricalRecords
from utils.models import TimeStampedModel

class ExpenseItem(models.Model):
    expense = models.ForeignKey('Expense', on_delete=models.CASCADE, related_name='expense_items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Cantidad Vendida')
    created_by = models.ForeignKey(CustomUser, related_name='expense_items_created', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(CustomUser, related_name='expense_items_updated', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()
    
    def get_cost(self):
        return self.inventory_item.price_category_sold * self.quantity

    class Meta:
        unique_together = ('expense', 'inventory_item')

class Expense(TimeStampedModel):
    expense_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Nombre del cliente')
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_by = models.ForeignKey(CustomUser, related_name='expenses_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='expenses_updated', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio', default=0.0)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.event})"

    def calculate_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.expense_items.all())
        return total_cost


