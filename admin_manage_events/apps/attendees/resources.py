# apps/attendees/resources.py
from .models import Purchase, Attendee
from import_export import resources, fields
from .models import Ticket
from import_export.widgets import ManyToManyWidget


class PurchaseResource(resources.ModelResource):
    attendees_info = fields.Field(
        column_name='attendees_info', 
        attribute='attendees', 
        widget=ManyToManyWidget(Attendee, field='name')
    )
    tickets_confirmed = fields.Field(
        column_name='tickets_confirmed', 
        attribute='tickets_confirmed'
    )

    class Meta:
        model = Purchase
        fields = ('purchase_id', 'buyer', 'event__title', 'ticket_category__name', 'company__name', 'attendees_info', 'tickets_confirmed')
        export_order = ('purchase_id', 'buyer', 'event__title', 'ticket_category__name', 'company__name', 'attendees_info', 'tickets_confirmed')
        import_id_fields = ('purchase_id',)
        skip_unchanged = True
        report_skipped = True

    def dehydrate_attendees_info(self, purchase):
        return ', '.join(f"{attendee.name} - {attendee.document_number}" for attendee in purchase.attendees.all())

    def dehydrate_tickets_confirmed(self, purchase):
        ticket_statuses = [str(ticket.ticket_confirmed) for ticket in purchase.ticket_set.all()]
        return ', '.join(ticket_statuses)

    def before_import_row(self, row, **kwargs):
        del row['buyer']
        del row['event__title']
        del row['ticket_category__name']
        del row['company__name']
        del row['attendees_info']

    def after_import_row(self, row, row_result, **kwargs):
        try:
            purchase_id = row.get('purchase_id')
            tickets_confirmed_data = row.get('tickets_confirmed')

            if purchase_id and tickets_confirmed_data:
                purchase = Purchase.objects.get(pk=purchase_id)
                ticket_status_list = [status.strip().lower() == 'true' for status in tickets_confirmed_data.split(',')]
                tickets = purchase.ticket_set.all()
                
                no_changes = True
                for ticket, status in zip(tickets, ticket_status_list):
                    if ticket.ticket_confirmed != status:
                        ticket.ticket_confirmed = status
                        ticket.save()
                        no_changes = False

                if no_changes:
                    row_result.import_type = row_result.IMPORT_TYPE_SKIP
                    # deshabilita el botón confirmar importación

        except Purchase.DoesNotExist:
            pass
        except Exception as e:
            raise e
        
