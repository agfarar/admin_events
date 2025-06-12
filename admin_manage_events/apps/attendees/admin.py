# apps/attendees/admin.py
from django.contrib import admin
from .models import Attendee
from .forms import AttendeeForm
from .models import Purchase, Attendee, Ticket
from .resources import PurchaseResource
from import_export.admin import ImportExportModelAdmin

class AttendeeAdmin(admin.ModelAdmin):
    form = AttendeeForm
    list_display = ('name', 'phone_number', 'created_at','updated_at')


    def get_form(self, request, obj=None, **kwargs):

        # 
        kwargs['form'] = AttendeeForm
        # 
        form = super(AttendeeAdmin, self).get_form(request, obj, **kwargs)
        # 
        form.user = request.user
        return form

    def get_queryset(self, request):
        #
        qs = super().get_queryset(request)
        # 
        try:
            if request.user.is_superuser:
                return qs
            # Hacer un query que filtre los eventos de los asistentes que pertenecen a la empresa del usuario que inició sesión
            return qs.filter(purchase__company=request.user.company)
            
            
        except Exception:
            return qs.none()
         
class TicketInline(admin.TabularInline):  
    model = Ticket  
    extra = 1  


class PurchaseAdmin(ImportExportModelAdmin):
    resource_class = PurchaseResource
    inlines = [TicketInline]
    list_display = ('purchase_id','buyer', 'event', 'ticket_category', 'company')
    list_filter = ('event', 'ticket_category', 'company')  # Añadir filtros por evento, categoría y empresa

    def get_import_resource_class(self):
        return PurchaseResource

    def get_export_resource_class(self):
        return PurchaseResource
    
    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = super().get_export_formats()
        return [f for f in formats if f().get_title() in ['csv', 'xlsx']]


admin.site.register(Purchase, PurchaseAdmin)  
admin.site.register(Attendee, AttendeeAdmin)  
admin.site.register(Ticket)  