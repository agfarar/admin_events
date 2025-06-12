# apps/events/forms.py
from django import forms
from .models import Event
from apps.inventory.models import InventoryItem

class InventoryItemInlineForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'add_stock', 'quantity_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.event_id:
            self.fields['id'].queryset = InventoryItem.objects.filter(event=self.instance.event_id)
        else:
            self.fields['id'].queryset = InventoryItem.objects.none()


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'is_paid_event', 'company','total_tickets']

    def __init__(self, *args, **kwargs):
        #
        super(EventForm, self).__init__(*args, **kwargs)


        self.fields['company'].initial = self.user.company.id

        if self.user.is_superuser:
            self.fields['company'].disabled = False
        else:
            self.fields['company'].disabled = True

