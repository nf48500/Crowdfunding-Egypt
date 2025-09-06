from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'country', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'country')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'country')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 'profile_picture',
                'birthdate', 'facebook_profile', 'country'
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name', 'phone',
                'birthdate', 'facebook_profile', 'country', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_age(self, obj):
        """Display user's age in admin list"""
        if obj.birthdate:
            return obj.get_age()
        return '-'
    get_age.short_description = 'Age'
