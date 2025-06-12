# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # si la compañia es nula, no se mostrara en la lista
    list_display = ('username', 'email', 'company', 'is_staff', 'is_active',)
    list_filter = ('username', 'email', 'company', 'is_staff', 'is_active',)
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'company')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'company', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    
    search_fields = ('username', 'email',)
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = "TIGGER"
admin.site.site_title = "TIGGER"
admin.site.index_title = "Bienvenidos al portal de administración"