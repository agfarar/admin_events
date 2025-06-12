# apps/attendees/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Purchase
from apps.events.models import EventTicketCategory
from django.core.exceptions import ValidationError

@receiver(pre_save, sender=Purchase)
def validate_ticket_availability(sender, instance, **kwargs):
    event_ticket_category = EventTicketCategory.objects.get(event=instance.event, ticket_category=instance.ticket_category)
    if event_ticket_category.tickets_sold >= event_ticket_category.tickets_available:
        raise ValidationError('No hay boletos disponibles para esta categoría.')
