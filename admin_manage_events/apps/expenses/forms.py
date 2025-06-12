# apps/expenses/forms.py
from django import forms
from .models import ExpenseItem, InventoryItem,Expense
from apps.events.models import Event
from accounts.models import CustomUser
from django.core.exceptions import ValidationError

class ExpenseItemForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Precio de Venta')

    class Meta:
        model = ExpenseItem
        fields = ['inventory_item', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['price'].initial = self.instance.inventory_item.price_category_sold

        self.fields['price'].widget.attrs['readonly'] = True

        inventory_items = InventoryItem.objects.filter(event__company=self.user.company.id, is_category_sold=True)
        choices = [('', '---------')]  # Añade esta línea para incluir un valor vacío por defecto
        choices += [(item.pk, f"{item.name} -- ${item.price_category_sold} (stock {item.quantity_available})") for item in inventory_items]
        self.fields['inventory_item'].choices = choices

        for item in inventory_items:
            self.fields['inventory_item'].widget.attrs[f'data-price-{item.pk}'] = str(item.price_category_sold)

    def clean_quantity(self):
        reduce_quantity = False
        if self.instance.pk and self.cleaned_data.get('quantity') < self.instance.quantity:
            reduce_quantity = True

        add_stock = self.cleaned_data.get('quantity')
        stock_actual = self.cleaned_data.get('inventory_item').quantity_available 

        # Validar que la cantidad a vender no sea mayor al stock actual siempre
        if add_stock > stock_actual and not reduce_quantity:
            raise ValidationError('Supeeraste el stock debes actualizar.')

        return add_stock


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [ 'event', 'name', 'company', 'date', 'description', 'amount']
    
    # permitee crear un campo de lectura en el formulario de creación de gastos
    # company_display = forms.CharField(disabled=True, required=False, label='Company') 


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['company_display'].initial = str(self.user.company)

        # Filtrar por la company del usuario que inicia sesión        
        self.fields['company'].initial = self.user.company
        self.fields['company'].disabled = True

        # self.fields['company'].widget = forms.HiddenInput()

        # No funciona con FK        
        # self.fields['company'].widget.attrs['readonly'] = True

        # Filtrar los eventos asociados al usuario que inicia sesión
        self.fields['event'].queryset = Event.objects.filter(company=self.user.company.id)
        
        # Filtrar el name del usuario que está asociado a la company
        self.fields['name'].queryset = CustomUser.objects.filter(company=self.user.company.id)

        self.fields['amount'].widget.attrs['readonly'] = True


        