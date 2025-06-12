# apps/attachments/admin.py


from django.contrib import admin
from .models import Attachment
from .forms import AttachmentForm

class AttachmentAdmin(admin.ModelAdmin):
    form = AttachmentForm
    list_display = ('name', 'file', 'company', 'created_at','updated_at')

    def get_form(self, request, obj=None, **kwargs):

        # 
        kwargs['form'] = AttachmentForm
        # 
        form = super(AttachmentAdmin, self).get_form(request, obj, **kwargs)
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
         

admin.site.register(Attachment,AttachmentAdmin)
