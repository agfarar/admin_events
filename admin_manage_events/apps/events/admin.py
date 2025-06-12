# apps/events/admin.py
from django.contrib import admin
from .models import Event, EventTicketCategory
from apps.inventory.models import InventoryItem
from .forms import EventForm, InventoryItemInlineForm

class EventTicketCategoryInline(admin.TabularInline):
    model = EventTicketCategory
    readonly_fields = ('tickets_sold',)
    extra = 1

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    fields = ('name', 'add_stock', 'category', 'is_category_sold','price','price_category_sold' ,'quantity_available', 'quantity_sold')
    readonly_fields = ('quantity_available','quantity_sold')
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.user = request.user
        return formset

class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ('title', 'company', 'start_time', 'end_time', 'created_at', 'total_tickets')
    inlines = [EventTicketCategoryInline, InventoryItemInline]

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = EventForm
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.is_superuser:
                return qs
            return qs.filter(company=request.user.company.id)
        except Exception:
            return qs.none()
        
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Ensure inventory items are linked to the event
        for formset in formsets:
            if isinstance(formset, InventoryItemInline):
                for form in formset:
                    if form.instance.pk is None:
                        form.instance.event = formset.instance
                        form.instance.save()

admin.site.register(Event, EventAdmin)
