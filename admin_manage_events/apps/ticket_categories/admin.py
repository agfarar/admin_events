# apps/ticket_categories/admin.py
from django.contrib import admin
from .models import TicketCategory,Company
from .forms import TicketCategoryForm

class TicketAdmin(admin.ModelAdmin):
    form = TicketCategoryForm
    list_display = ('name', 'company', 'price', 'created_at','updated_at')

    def get_form(self, request, obj=None, **kwargs):

        # 
        kwargs['form'] = TicketCategoryForm
        # 
        form = super(TicketAdmin, self).get_form(request, obj, **kwargs)
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
            return qs.filter(company=request.user.company.id)
        except Exception:
            return qs.none()
         

admin.site.register(TicketCategory,TicketAdmin)

class CompanyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.is_superuser:
                return qs
            return qs.filter(id=request.user.company.id)
        except Exception:
            return qs.none()

admin.site.register(Company, CompanyAdmin)
