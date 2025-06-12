# apps/attendees/forms.py
from django import forms
from .models import Attendee

class AttendeeForm(forms.ModelForm):

    class Meta:
        model = Attendee 
        fields = '__all__'
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/intl-tel-input@17.0.3/build/css/intlTelInput.css',
                    'css/phone_number.css')
        }

        js = (
            'https://cdn.jsdelivr.net/npm/intl-tel-input@17.0.3/build/js/intlTelInput.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.3/js/intlTelInput.min.js',
            'js/phone_number_init.js',  # Archivo JS personalizado
        )

    def __init__(self, *args, **kwargs):
        super(AttendeeForm, self).__init__(*args, **kwargs)

        if self.user.is_superuser:
            print("Superuser")
            # self.fields['company'].disabled = False
        else:
            print("corregir")
            # self.fields['event'].queryset = self.fields['event'].queryset.filter(company=self.user.company)
            # self.fields['ticket_category'].queryset = self.fields['ticket_category'].queryset.filter(company=self.user.company)
            # self.fields['attachment'].queryset = self.fields['attachment'].queryset.filter(company=self.user.company)
            # self.fields['company'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')

        # Verificar si el campo de teléfono está presente y tiene un valor
        if phone_number:
            # Obtener el número completo (incluyendo el prefijo de marcación)
            full_number = self.cleaned_data.get('phone_number')

            # Verifica que solo contenga numero y el signo +
            if not full_number.replace('+', '').isdigit():
                self.cleaned_data['phone_number'] = '+'
                self.add_error('phone_number', 'El número de teléfono solo puede contener números y el signo +.')

            # Verificar si el número no tiene el prefijo de marcación
            if not full_number.startswith('+'):
                self.cleaned_data['phone_number'] = '+'
                self.add_error('phone_number', 'Debe incluir el prefijo de marcación internacional.')

        return cleaned_data