# apps/events/models.py
from accounts.models import CustomUser
from django.db import models
from utils.models import TimeStampedModel
from apps.ticket_categories.models import TicketCategory, Company
from simple_history.models import HistoricalRecords

class Event(TimeStampedModel):
    event_id = models.AutoField(primary_key=True, verbose_name='ID del Evento')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    location = models.CharField(max_length=255, verbose_name='Ubicación')
    start_time = models.DateTimeField(verbose_name='Fecha y Hora de Inicio')
    end_time = models.DateTimeField(verbose_name='Fecha y Hora de Finalización')
    is_paid_event = models.BooleanField(default=False, verbose_name='Evento Pagado')
    total_tickets = models.IntegerField(verbose_name='Total de Tickets para el evento', default=0)
    ticket_categories = models.ManyToManyField(TicketCategory, through='EventTicketCategory')
    created_by = models.ForeignKey(CustomUser, related_name='events_created', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='events_updated', on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.title

class EventTicketCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, verbose_name='Categoría ticket')
    tickets_available = models.IntegerField(verbose_name='Tickets asignados por categoría', default=0)
    tickets_sold = models.PositiveIntegerField(verbose_name='Tickets vendidos', default=0)

    class Meta:
        verbose_name = 'Categoría de Ticket para Evento'
        verbose_name_plural = 'Categorías de Tickets para Eventos'
        unique_together = ('event', 'ticket_category')

    def __str__(self):
        return f"{self.event.title} - {self.ticket_category.name} ({self.tickets_available} tickets)"
