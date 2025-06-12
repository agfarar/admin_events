# apps/inventory/admin.py
from django.contrib import admin
from .models import InventoryItem
from .forms import InventoryItemForm

class InventoryItemAdmin(admin.ModelAdmin):
    form = InventoryItemForm
    model = InventoryItem
    fields = ('event', 'name','category', 'add_stock', 'is_category_sold' ,'quantity_available','quantity_sold','price','price_category_sold')
    list_display = ('name', 'event', 'category', 'quantity_available', 'quantity_sold', 'price', 'price_category_sold', 'is_category_sold', 'created_by', 'updated_by')
    readonly_fields = ('quantity_sold', 'quantity_available')

    def get_fields(self, request, obj=None):
        """ obtiene los campos del modelo InventoryItem y los muestra en el admin
        ademas si el item boleano is_category_sold es falso, no muestra los campos quantity_sold y prince_category_sold

        Args:
            request (<class 'django.core.handlers.wsgi.WSGIRequest'>): contiene los datos de la solicitud del cliente al servidor
            obj (<class 'apps.inventory.models.InventoryItem'>, optional): objeto de la clase InventoryItem. Defaults to None.

        Returns:
            class list: lista de campos del modelo InventoryItem
        """
        # super llama al metodo get_fields de la clase padre para obtener los campos del modelo InventoryItem
        fields = list(super().get_fields(request, obj))
        if obj is None or not obj.is_category_sold:
            if 'quantity_sold' in fields:
                fields.remove('quantity_sold')
            if 'prince_category_sold' in fields:
                fields.remove('prince_category_sold')

        return fields

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        # Aquí se modifica la función de inicialización del formulario para incluir el usuario
        return lambda *args, **kwargs: Form(*args, **kwargs, user=request.user)

    # def save_model(self, request, obj, form, change):
    #     # Lógica personalizada específica del admin antes de guardar el objeto
    #     super().save_model(request, obj, form, change)
    #     # Lógica personalizada específica del admin después de guardar el objeto
    #     # TODO: REVISAR ESTO
    #     if 'add_stock' in form.changed_data:
    #         obj.update_stock(obj.add_stock)
    #     obj.save()

admin.site.register(InventoryItem, InventoryItemAdmin)
