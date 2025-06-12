# apps/attachments/forms.py

from django import forms
from .models import Attachment

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        # todos los campos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        #
        super(AttachmentForm, self).__init__(*args, **kwargs)

        # Obtener la empresa del usuario
        self.fields['company'].initial = self.user.company.id

        if self.user.is_superuser:
            self.fields['company'].disabled = False
        else:
            # filtrar solo mis eventos
            self.fields['event'].queryset = self.fields['event'].queryset.filter(company=self.user.company)
            self.fields['company'].disabled = True