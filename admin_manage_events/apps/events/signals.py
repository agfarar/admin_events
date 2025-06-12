# apps/events/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EventTicketCategory,Event
from apps.inventory.models import InventoryItem
from apps.attendees.models import Ticket


@receiver(post_save, sender=Event)
def update_inventory_on_event_save(sender, instance, **kwargs):
    # Ejemplo de cómo podrías actualizar el inventario cuando se guarda un evento.
    # Ajusta según la lógica de tu negocio.
    for inventory_item in instance.inventory_items.all():
        print(inventory_item)  # Esto es solo para depuración, puedes eliminarlo en producción.
        # Añadir en quantity_available la cantidad de add_stock
        inventory_item.quantity_available += inventory_item.add_stock
        inventory_item.save() 

@receiver(post_delete, sender=Event)
def update_inventory_on_event_delete(sender, instance, **kwargs):
    # captro los elementos del inventario asociados al evento
    inventory_items = InventoryItem.objects.filter(event=instance)
    for inventory_item in inventory_items:
        print(inventory_item)      
        # Ajusta el stock según el evento eliminado
        inventory_item.quantity_available += inventory_item.quantity_used
        inventory_item.save()

    

@receiver(post_save, sender=Ticket)
def update_tickets_sold_on_save(sender, instance, **kwargs):
    event_ticket_category = EventTicketCategory.objects.get(event=instance.purchase.event, ticket_category=instance.purchase.ticket_category)
    event_ticket_category.tickets_sold = Ticket.objects.filter(purchase__event=instance.purchase.event, purchase__ticket_category=instance.purchase.ticket_category).count()
    event_ticket_category.save()

@receiver(post_delete, sender=Ticket)
def update_tickets_sold_on_delete(sender, instance, **kwargs):
    event_ticket_category = EventTicketCategory.objects.get(event=instance.purchase.event, ticket_category=instance.purchase.ticket_category)
    event_ticket_category.tickets_sold = Ticket.objects.filter(purchase__event=instance.purchase.event, purchase__ticket_category=instance.purchase.ticket_category).count()
    event_ticket_category.save()
