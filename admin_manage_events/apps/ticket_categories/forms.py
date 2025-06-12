# apps/ticket_categories/forms.py
from django import forms
from .models import TicketCategory

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['name', 'price','company']

    def __init__(self, *args, **kwargs):
        #
        super(TicketCategoryForm, self).__init__(*args, **kwargs)

        # Obtener la empresa del usuario
        self.fields['company'].initial = self.user.company.id

        if self.user.is_superuser:
            self.fields['company'].disabled = False
        else:
            # filtrar solo mis eventos
            # self.fields['event_id'].queryset = self.fields['event_id'].queryset.filter(company=self.user.company)
            self.fields['company'].disabled = True