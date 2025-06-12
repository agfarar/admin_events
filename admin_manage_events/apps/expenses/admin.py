from django.contrib import admin
from .models import Expense, ExpenseItem
from .forms import ExpenseItemForm, ExpenseForm
from apps.inventory.models import InventoryItem

class ExpenseItemInline(admin.TabularInline):
    model = ExpenseItem
    form = ExpenseItemForm
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ExpenseItemInline, self).get_formset(request, obj, **kwargs)
        formset.form.user = request.user
        return formset

class ExpenseAdmin(admin.ModelAdmin):
    model = Expense
    form = ExpenseForm
    # fields = ('name', 'event', 'company', 'date', 'description', 'amount')
    list_display = ('name', 'amount', 'event', 'company', 'date', 'created_by', 'updated_by')
    inlines = [ExpenseItemInline]

    class Media:
        js = ('js/expense_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExpenseAdmin, self).get_form(request, obj, **kwargs)
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

    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:
    #         obj.created_by = request.user
    #     obj.updated_by = request.user
    #     super().save_model(request, obj, form, change)


    def save_formset(self, request, form, formset, change):
        if formset.model == ExpenseItem:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk:
                    instance.created_by = request.user
                instance.updated_by = request.user
                

                # query que filtra la tabla inventory por el id del item y el id del evento
                inventory_item = InventoryItem.objects.filter(id=instance.inventory_item.id, event=instance.expense.event)

                # validamos si el usuario edita la cantidad solo debe añadirse la diferencia
                if change:
                    # query que filtra la tabla expense_item por el id del item
                    expense_item = ExpenseItem.objects.get(id=instance.id)
                    # validamos si la cantidad es mayor a la cantidad anterior
                    if instance.quantity > expense_item.quantity:
                        # recorre el query y actualiza la cantidad vendida de cada item y actualiza restando el stock disponible
                        for item in inventory_item:
                            item.quantity_sold += instance.quantity - expense_item.quantity
                            item.quantity_available -= instance.quantity - expense_item.quantity
                            item.save(expenses_save=True)
                    # validamos si la cantidad es menor a la cantidad anterior
                    elif instance.quantity < expense_item.quantity:
                        # recorre el query y actualiza la cantidad vendida de cada item y actualiza sumando el stock disponible
                        for item in inventory_item:
                            item.quantity_sold -= expense_item.quantity - instance.quantity
                            item.quantity_available += expense_item.quantity - instance.quantity
                            item.save(expenses_save=True)
                    else:
                        print("prueba")
                else:
                    # recorre el query y actualiza la cantidad vendida de cada item y actualiza restando el stock disponible
                    for item in inventory_item:
                        item.quantity_sold += instance.quantity
                        item.quantity_available -= instance.quantity
                        item.save(expenses_save=True)
                instance.save()
            formset.save_m2m()
        else:
            formset.save()

admin.site.register(Expense, ExpenseAdmin)
