from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


r"""
  ____          _                  _   _
 / ___|   _ ___| |_ ___  _ __ ___ | | | |___  ___ _ __
| |  | | | / __| __/ _ \| '_ ` _ \| | | / __|/ _ \ '__|
| |__| |_| \__ \ || (_) | | | | | | |_| \__ \  __/ |
 \____\__,_|___/\__\___/|_| |_| |_|\___/|___/\___|_|

    _       _           _
   / \   __| |_ __ ___ (_)_ __
  / _ \ / _` | '_ ` _ \| | '_ \
 / ___ \ (_| | | | | | | | | | |
/_/   \_\__,_|_| |_| |_|_|_| |_|

"""
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    r"""
    Register custom user model admin. Extends Django's UserAdmin class.
    """
    fieldsets = (
        ('Credentials', {'fields': ('username', 'password')}),
        ('Name', {'fields': ('first_name', 'last_name')}),
        ('Contact Info', {'fields': ('email', 'phone', 'provider')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone', 'last_login', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ['groups']
    ordering = ['last_name', 'first_name']

    def get_form(self, request, obj=None, **kwargs):
        r"""
        Restrict what staff users with permission to edit User model instances can do.  

        See [What You Need to Know to Manage Users in Django Admin](https://realpython.com/manage-users-in-django-admin/)
        """
        ## Instantiate variables.
        # Get the default form for the admin add/change view.
        form = super().get_form(request, obj, **kwargs)
        # Get is_superuser status for the current user (extracted from the request parameter).
        is_superuser = request.user.is_superuser
        # The disabled_fields set will be used to store fields that need to be disabled in the admin
        # add/change form.
        disabled_fields = set()  

        ## Prevent non-superusers from editing fields only superusers should have access to.
        if not is_superuser:       
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions',
            }
        
        ## Prevent non-superusers to modify fields of superusers.  
        if (not is_superuser 
            and obj is not None
            and obj.is_superuser
        ):
            disabled_fields |= {
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }
        
        ## Prevent non-superusers from editing their own permissions.
        if (not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        ## Disable those fields found in the disabled_fields set.
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        ## Return the form.
        return form    

