# apps/attendees/models.py
from django.db import models
from apps.ticket_categories.models import TicketCategory,Company
from apps.events.models import Event, EventTicketCategory
from apps.attachments.models import Attachment
from utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

#name 'ValidationError' is not defined


# Esta tabla manejará la información de las compras realizadas por los usuarios,
class Purchase(TimeStampedModel):
    purchase_id = models.AutoField(primary_key=True)  # Identificador único para cada compra
    buyer = models.CharField(max_length=255,verbose_name='Nombres Comprador')  # Nombre del comprador
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Empresa')  # Evento asociado a la compra
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, verbose_name='Categoría Ticket')  # Categoría del boleto
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')  # Empresa asociada
    # attendees = models.ManyToManyField(Attendee)  # Relación ManyToMany con Attendee a través del modelo intermedio Ticket
    attendees = models.ManyToManyField('Attendee', through='Ticket', verbose_name='Asistentes')  # Relación ManyToMany con Attendee a través del modelo intermedio Ticket


    class Meta:
        verbose_name = 'Compra'  # Nombre singular para el modelo en la interfaz de administración
        verbose_name_plural = 'Compras'  # Nombre plural para el modelo en la interfaz de administración

    def __str__(self):
        return f"{self.buyer} - {self.event} - {self.ticket_category.name}"  # Representación en cadena del modelo
        
    def clean(self):
        # ingresa primero aquí antes que los signals para asegurarse que se tiene el numero ded boletos
        event_ticket_category = EventTicketCategory.objects.get(event=self.event, ticket_category=self.ticket_category)
        if event_ticket_category.tickets_sold >= event_ticket_category.tickets_available:
            raise ValidationError('No hay boletos disponibles para esta categoría.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Esta tabla manejará la información de los asistentes a los eventos, 
# la cual es ingresada por el creador del evento.
class Attendee(TimeStampedModel):
    attendee_id = models.AutoField(primary_key=True)  # Identificador único para cada asistente
    name = models.CharField(max_length=255,verbose_name='Nombres Asistente' )  # Nombre del asistente
    email = models.EmailField(verbose_name='Correo')  # Correo electrónico del asistente
    DOCUMENT_TYPE_CHOICES = [
        ('DNI', 'DNI'),
        ('Pasaporte', 'Pasaporte'),
        ('Carné de Extranjería', 'Carné de Extranjería'),
        ('Otros', 'Otros'),
    ]
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='DNI', verbose_name='Tipo documento')
    document_number = models.CharField(max_length=100,verbose_name='Número Documento')
    phone_number = models.CharField(max_length=100, verbose_name='Teléfono')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')  # Dirección (opcional)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Fecha Nacimiento')  # Fecha de nacimiento (opcional)
    GENDER_CHOICES = [  # Opciones para el campo de género
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Género')  # Género (opcional)
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Recibo Compra')  # Archivo adjunto (opcional)

    class Meta:
        verbose_name = 'Asistente'  # Nombre singular para el modelo en la interfaz de administración
        verbose_name_plural = 'Asistentes'  # Nombre plural para el modelo en la interfaz de administración

    def __str__(self):
        return f"{self.name} ({self.document_type}: {self.document_number})"  # Representación en cadena del modelo


class Ticket(TimeStampedModel):
    ticket_id = models.AutoField(primary_key=True)  # Identificador único para cada boleto
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, verbose_name='Compra')  # Relación con la compra
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, verbose_name='Asistente')  # Relación con el asistente
    ticket_confirmed = models.BooleanField(default=False, verbose_name='Ticket Confirmado')  # Indica si el boleto está confirmado
    ticket_owner = models.BooleanField(default=False, verbose_name='Titular Ticket')  # Indica quien el comprador del boleto
    ticket_send_by_email = models.BooleanField(default=False, verbose_name='Ticket por correo')  # Indica si el boleto fue enviado por correo electrónico
    

    class Meta:
        verbose_name = 'Boleto'  # Nombre singular para el modelo en la interfaz de administración
        verbose_name_plural = 'Boletos'  # Nombre plural para el modelo en la interfaz de administración

    def __str__(self):
        return f"Boleto para {self.attendee.name} (Compra: {self.purchase.buyer})"  # Representación en cadena del modelo
