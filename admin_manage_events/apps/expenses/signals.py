# apps/expenses/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Expense, ExpenseItem
from apps.inventory.models import InventoryItem

@receiver(post_save, sender=Expense)
def update_inventory_on_expense_save(sender, instance, created, **kwargs):
    if created:
        for expense_item in ExpenseItem.objects.filter(expense=instance):
            inventory_item = expense_item.inventory_item
            inventory_item.use_stock(expense_item.quantity)
            inventory_item.quantity_sold += expense_item.quantity
            inventory_item.save()

# @receiver(pre_save, sender=Expense)
# def update_inventory_on_expense_edit(sender, instance, **kwargs):
#     if instance.pk:  # Verificar si ya existe (edición)
#         previous_instance = Expense.objects.get(pk=instance.pk)
#         if previous_instance:
#             for previous_expense_item in ExpenseItem.objects.filter(expense=previous_instance):
#                 inventory_item = previous_expense_item.inventory_item
#                 inventory_item.quantity_available += previous_expense_item.quantity
#                 inventory_item.quantity_sold -= previous_expense_item.quantity
#                 inventory_item.save()
#             for current_expense_item in ExpenseItem.objects.filter(expense=instance):
#                 inventory_item = current_expense_item.inventory_item
#                 inventory_item.use_stock(current_expense_item.quantity)
#                 inventory_item.quantity_sold += current_expense_item.quantity
#                 inventory_item.save()
