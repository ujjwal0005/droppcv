from django.contrib import admin
from .models import User, EmployeeProfile, EmployerProfile, Service

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_staff', 'is_superuser','user_type')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'user_type')
    search_fields = ('email', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name','image', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('name','image', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'service_type', 'work_experience', 'salary_expectation')
    search_fields = ('user__email', 'location', 'service_type')
    list_filter = ('location', 'service_type')

class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'location', 'work_experience')
    search_fields = ('user__email', 'company_name', 'location')
    list_filter = ('location',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Register models
admin.site.register(User, UserAdmin)
admin.site.register(EmployeeProfile, EmployeeProfileAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)
admin.site.register(Service, ServiceAdmin)
