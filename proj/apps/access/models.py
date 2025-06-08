from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

PHONE_SERVICE = [
    ('mms.att.net'              ,  'AT&T'),
    ('myboostmobile.com'        ,  'Boost Mobile'),
    ('mms.cricketwireless.net'  ,  'Cricket Wireless'),
    ('msg.fi.google.com'        ,  'Google Project Fi'),
    ('text.republicwireless.com',  'Republic Wireless'),
    ('pm.sprint.com'            ,  'Sprint'),
    ('mypixmessages.com'        ,  'Straight Talk'),
    ('tmomail.net'              ,  'T-Mobile'),
    ('message.ting.com'         ,  'Ting'),
    ('mmst5.tracfone.com'       ,  'Tracfone'),
    ('mms.uscc.net'             ,  'U.S. Cellular'),
    ('vzwpix.com'               ,  'Verizon'),
    ('vmpix.com'                ,  'Virgin Mobile'),
]
PHONE_SERVICE_WITH_BLANK = [('', '--------')]
for item in PHONE_SERVICE: PHONE_SERVICE_WITH_BLANK.append(item)

class User(AbstractUser):
    r"""
    The `User` model is an abstraction of the standard Django `User` model.  It adds the following 
    fields:

    - `email`: User's email address.
    - `phone`: User's mobile phone number.
    - `provider`: The cellular network provider for the user's mobile number. Used for text messaging.
    
    Otherwise it is identical to the Django default ``User`` model.
    """
    
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False,
        help_text=_('Unique email address for the user.  Can be used in place of username for login purposes.'))
    phone = models.CharField(_('phone number'), max_length=20, null=True, blank=True,
        help_text=_('Mobile cell number (used for text messaging).'))
    provider = models.CharField(_('service provider'), max_length=100, null=True, blank=True, choices=PHONE_SERVICE, 
        help_text=_('Cell phone provider is needed for sending text messages.'))

    def has_access(self, obj, add_attr=True):
        r"""
        Determine if the user has frontend update access to change a model or model instance.  
        Returns True if the user has update access, False otherwise.  If a model instance is 
        provided, the instance is modified with a `user_has_access` attribute that reports the same 
        True or False value. Per instance access is supported if the model defines `Group` field 
        like so:

        ```python
        from django.contrib.auth.models import Group

        class Page(models.Model):
            groups = models.ManyToManyField(Group, blank=True)
        ```

        The algorithm works like so:

        - If the user is superuser, access is automatically granted.
        - If the user is not a staff member access is automatically rejected.
        - Only if the user is a staff member is access checked. 

        Staff member access rules vary depending on if the `obj` is an model instance or model 
        class.  If `obj` is a model instance:

        1. Check that the user has admin `change` permission for the model class via the standard 
           Django permissions API.  If yes, grant access.  If no, continue to 2.
        2. If instance does not have `groups` attribute, reject access.  Else, go to 3.
        3. See if user and instance share any groups.  If so, grant access  Else, reject.

        If `obj` is a model class:

        1. Check that the user has admin `change` permission for the model class via the standard 
           Django permissions API.  If yes, grant access.  If no, reject.

        Using this code, you could define a `Page` instance that only select staff members can 
        access.  To check for user access on a model instance, do something like this:
        
        ```python
        page = Page.object.get(pk=14)
        if user.has_access(page):
            print("Access to page granted!") 
        ```
        
        In the above example, `page` is monkey patched to now include the `user_has_access` 
        attribute.  So after calling `user.has_access(page)` this works as well:
        
        ```python
        if page.user_has_access:
            print("Access to page granted!")
        ```

        You can override this option (such that the `user_has_access` attribute is not monkey 
        patched to the instance) by setting the `add_attr` argument to False.  It is defaulted to 
        True.

        The object passed in need not be a model instance.  It can be a model, e.g. `Page`:

        ```python
        if user.has_access(Page):
            print("Access to Page model granted!") 
        ```

        But because the object is a model, no `has_access` attribute can be, or will be, affixed to 
        the model i.e. `Page.user_has_access` will return an error.  After all, you can't monkey
        patch a class, just an instance of a class.

        """

        perm = None
        inst = None
        is_instance = False

        # Is obj a model or a model instance?  Don't know of an official way to do this in Django.
        # I found that `type(obj.id)` is `int` if a model instance.  (If a model, `type(obj.id)`
        # returns `django.db.models.query_utils.DeferredAttribute`.  Just FYI.)
        is_instance = type(obj.id) == int
        if is_instance: inst = obj

        # Get the change model permission name (e.g. 'master.change_post').
        perm = f'{obj._meta.app_label}.change_{obj._meta.verbose_name}'

        # If user is not active, reject access request.
        if not self.is_active: 
            if is_instance and add_attr: setattr(inst, 'user_has_access', False)
            return False

        # If user is a superuser, grant access request. (Superusers don't need to have group 
        # affiliation to modify.)
        if self.is_superuser: 
            if is_instance and add_attr: setattr(inst, 'user_has_access', True)
            return True

        # If user is not staff, reject access request.
        if not self.is_staff: 
            if is_instance and add_attr: setattr(inst, 'user_has_access', False)
            return False

        # Value `perm` is the standard Django model change permissions (e.g. 'master.change_page').  
        # Check to see if user has Django model change permission.  If so grant access request.
        if self.has_perm(perm):
            if is_instance and add_attr: setattr(inst, 'user_has_access', True)
            return True
        # If obj is a model then reject access request because self.has_perm(perm) from above
        # returned False.  Note, we don't reject access if obj is a model instance as we have 
        # not yet checked instance access. 
        else:
            if not is_instance:
                return False

        # If inst is defined ...
        if is_instance:
            # If the `groups` field is not defined for the model, reject access.  
            if not hasattr(inst, 'groups'): 
                if add_attr: setattr(inst, 'user_has_access', False)
                return False
            # Check to see if user group set and the instance group set have at least one common
            # group.  If so, grant access.  Else, request access.
            user_has_inst_group = any(group in inst.groups.all() for group in self.groups.all())
            if add_attr: setattr(inst, 'user_has_access', user_has_inst_group)
            return user_has_inst_group
        # Should be impossible get here, but more explicit if included.  
        else: # pragma: no cover
            return False # pragma: no cover
        
        # Should be impossible get here, but more explicit if included.
        return False # pragma: no cover

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'

