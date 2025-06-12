# apps/inventory/forms.py
from django import forms
from .models import InventoryItem
from django.core.exceptions import ValidationError
from apps.events.models import Event

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['event', 'name', 'add_stock','category', 'is_category_sold','quantity_sold']


    # class Media:
    #     js = ('js/format_numbers.js',)
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Aquí puedes usar self.user para personalizar el formulario
        # self.fields['price'].widget = forms.TextInput(attrs={'type': 'text'})
        # self.fields['price_category_sold'].widget = forms.TextInput(attrs={'type': 'text'})
        
        # Filtrar los eventos asociados al usuario que inicia sesión
        self.fields['event'].queryset = Event.objects.filter(company=self.user.company.id)
        


    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk and self.user:
            instance.created_by = self.user
        if self.user:
            instance.updated_by = self.user
        if commit:
            instance.save()
        return instance

    def clean_add_stock(self):
        # # validamos el campo add_stock si es negativo reste a quantity_available
        # if self.add_stock < 0 and self.quantity_available < abs(self.add_stock):
        #     # mostramos error en el campo de add_stock si no hay suficiente stock disponible
        #     raise forms.add_stock.ValidationError("No hay suficiente stock disponible")

        add_stock = self.cleaned_data.get('add_stock')
        # Suponiendo que 'stock_actual' es el campo en tu modelo que tiene el stock actual
        stock_actual = self.instance.quantity_available

        if add_stock < 0 and abs(add_stock) > stock_actual:
            raise ValidationError('No puedes eliminar más stock del que existe.')

        return add_stock

    # def clean_price(self):
    #     price = self.cleaned_data.get('price')
    #     return int(str(price.replace('.', '')))

    # def clean_price_category_sold(self):
    #     price_category_sold = self.cleaned_data.get('price_category_sold')
    #     return int(str(price_category_sold.replace('.', '')))

    # # capturamos el error que se genera desde el modelo save
    # def clean(self):
    #     cleaned_data = super().clean()
    #     add_stock = cleaned_data.get('add_stock')
    #     quantity_available = cleaned_data.get('quantity_available')
    #     raise forms.ValidationError("No hay suficiente stock disponible")
    #     # return cleaned_data

    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:
    #         obj.created_by = request.user
    #     obj.updated_by = request.user
    #     if 'add_stock' in form.changed_data:
    #         obj.update_stock(obj.add_stock)
    #     obj.save()