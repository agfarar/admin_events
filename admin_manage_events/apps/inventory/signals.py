# apps/inventory/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.expenses.models import Expense
from .models import InventoryItem


# @receiver(post_save, sender=Expense)
# def update_inventory_on_expense_save(sender, instance, **kwargs):
#     if instance.inventory_item:
#         # añadir el add_stock al quantity_available
#         instance.inventory_item.quantity_available += instance.add_stock
#         instance.inventory_item.save()

# @receiver(post_delete, sender=Expense)
# def update_inventory_on_expense_delete(sender, instance, **kwargs):
#     if instance.inventory_item:
#         instance.inventory_item.quantity_used -= 1
#         instance.inventory_item.save()

# @receiver(post_save, sender=Revenue)
# def update_inventory_on_revenue_save(sender, instance, **kwargs):
#     if instance.inventory_item:
#         instance.inventory_item.quantity_sold += 1
#         instance.inventory_item.save()

# @receiver(post_delete, sender=Revenue)
# def update_inventory_on_revenue_delete(sender, instance, **kwargs):
#     if instance.inventory_item:
#         instance.inventory_item.quantity_sold -= 1
#         instance.inventory_item.save()
