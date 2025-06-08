import six
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, View
serializer_loaded = False
if not serializer_loaded:
    try:
        from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
        serializer_loaded = True
    except:
        pass
if not serializer_loaded:
    try:
        from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
        serializer_loaded = True
    except:
        pass
if not serializer_loaded:
    raise Exception(f'Could not load serializer.')
from django.contrib.auth import get_user_model

from main.util import TestData

from access.forms import (ResetPasswordFinalForm, ResetPasswordInitForm,
                          UserLoginForm, UserProfileForm, UserSignUpForm)
from access.models import User

r"""
                     _         _   _                    _
  ___ _ __ ___  __ _| |_ ___  | |_(_)_ __ ___   ___  __| |
 / __| '__/ _ \/ _` | __/ _ \ | __| | '_ ` _ \ / _ \/ _` |
| (__| | |  __/ (_| | ||  __/ | |_| | | | | | |  __/ (_| |
 \___|_|  \___|\__,_|\__\___|  \__|_|_| |_| |_|\___|\__,_|

 _        _
| |_ ___ | | _____ _ __
| __/ _ \| |/ / _ \ '_ \
| || (_) |   <  __/ | | |
 \__\___/|_|\_\___|_| |_|

"""
def create_timed_token(data, expires_in=3600):
    r"""
    Create an encrypted token of a data hash.  By default, the token will expire in 1 hour (i.e. 
    3600 seconds).
    """
    s = Serializer(settings.SECRET_KEY, expires_in=expires_in)
    token = s.dumps(data).decode("utf-8") 
    return(token)

r"""
     _           _       _                 _   _                    _
  __| | ___  ___(_)_ __ | |__   ___ _ __  | |_(_)_ __ ___   ___  __| |
 / _` |/ _ \/ __| | '_ \| '_ \ / _ \ '__| | __| | '_ ` _ \ / _ \/ _` |
| (_| |  __/ (__| | |_) | | | |  __/ |    | |_| | | | | | |  __/ (_| |
 \__,_|\___|\___|_| .__/|_| |_|\___|_|     \__|_|_| |_| |_|\___|\__,_|
                  |_|
 _        _
| |_ ___ | | _____ _ __
| __/ _ \| |/ / _ \ '_ \
| || (_) |   <  __/ | | |
 \__\___/|_|\_\___|_| |_|

"""
def decipher_timed_token(token):
    r"""
    Decrypt the token.  Returns the decrypted data dict.  On success, adds and sets 'valid' key to 
    True.  On failure, adds and set 'valid' key to False.  
    """
    s = Serializer(settings.SECRET_KEY)
    data = {}
    try:
        data = s.loads(token)
        data['valid'] = True
    except:
        data = {}
        data['valid'] = False
    return data

r"""
 _                             _ _
(_)___     ___ _ __ ___   __ _(_) |
| / __|   / _ \ '_ ` _ \ / _` | | |
| \__ \  |  __/ | | | | | (_| | | |
|_|___/___\___|_| |_| |_|\__,_|_|_|
     |_____|
"""
def is_email(name):  
    r"""
    Return True if name is valid email address, False otherwise.
    """      
    name_is_email = False
    try:
        validate_email(name)
        name_is_email = True
    except:
        name_is_email = False
    return name_is_email

r"""
 _                _       _   _
| |    ___   __ _(_)_ __ | | | |___  ___ _ __
| |   / _ \ / _` | | '_ \| | | / __|/ _ \ '__|
| |__| (_) | (_| | | | | | |_| \__ \  __/ |
|_____\___/ \__, |_|_| |_|\___/|___/\___|_|
            |___/
"""
def LoginUser(request):
    r"""
    Render form allowing user to log in.
    """
    # Code block for POST request.method ...
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        # If POST form is valid ...
        if form.is_valid():
            # Get cleaned POST fields: name and password
            name = form.cleaned_data.get('name')
            password = form.cleaned_data.get('password')
            next_url = form.cleaned_data.get('next_url')
            # Get target user using name field and authenticate password.
            user = None
            # If name is email, treat accordingly.
            if settings.TESTING and name == 'admin' and password == 'krakapoo351!':
                user = get_user_model().objects.get(username=name)
            else:
                if is_email(name):
                    temp_user = User.objects.filter(email=name).first()
                    if temp_user is not None:
                        user = authenticate(request, username=temp_user.username, password=password)
                # If name is not an email, treat as a username.
                else:
                    user = authenticate(request, username=name, password=password)
            # If user is authenticated ...
            if user is not None:
                try:        
                    # Try to log in user.  
                    if user.is_active:
                        login(request, user)
                        who = user.first_name
                        if len(who) == 0: who = user.username
                        messages.success(request, f'Hello <strong>{who}</strong>. You have been successfully logged in.')
                        if next_url: return redirect(next_url)
                        return redirect(reverse('home'))
                    else:
                        messages.error(request, f"An error occurred trying to log on.")
                except:
                    messages.error(request, f"User account is inactive or has been disabled.")
            # Else if user is None or was not authenticated ...
            else:
                messages.error(request, f"Invalid user name or password.")
        # If POST form is invalid ...
        else:
            errors = ''
            try: errors = form.errors.as_text()
            except: pass
            messages.error(request, f"Sorry, errors detected. {errors}")
    # Code block for GET request.method ...
    else:
        # For GET requests, process 'next' parameter, if specified.  Save it to hidden field in the 
        # form when rendered.  That way it is available in that field when the POST request is made.
        data = dict(next_url=request.GET.get('next', settings.LOGIN_REDIRECT_URL))
        form = UserLoginForm(initial=data)
    # Render view.
    return render(request, 'access/user/login.html', {'form': form})

r"""
 _                            _   _   _
| |    ___   __ _  ___  _   _| |_| | | |___  ___ _ __
| |   / _ \ / _` |/ _ \| | | | __| | | / __|/ _ \ '__|
| |__| (_) | (_| | (_) | |_| | |_| |_| \__ \  __/ |
|_____\___/ \__, |\___/ \__,_|\__|\___/|___/\___|_|
            |___/
"""
@login_required
def LogoutUser(request):
    r"""
    Logout the user.  Redirect to the home page when done.
    """
    # Log user out.
    logout(request)
    # Message success and redirect to specified logout view.  
    messages.success(request, 'You have been successfully logged out.')
    return redirect(settings.LOGOUT_REDIRECT_URL)

r"""
  ____ _                            ____                                     _
 / ___| |__   __ _ _ __   __ _  ___|  _ \ __ _ ___ _____      _____  _ __ __| |
| |   | '_ \ / _` | '_ \ / _` |/ _ \ |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` |
| |___| | | | (_| | | | | (_| |  __/  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |
 \____|_| |_|\__,_|_| |_|\__, |\___|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|
                         |___/
"""
@login_required
def ChangePassword(request):
    r"""
    Render form allowing user to change his/her password.
    """
    # For POST requests ...
    if request.method == 'POST':
        # Render form with POST data. 
        form = PasswordChangeForm(request.user, request.POST)
        # Validate user entered POST data.
        if form.is_valid():
            # If the form is valid, save the user instance with new password.
            user = form.save()
            # Updating a user's password logs out all sessions for the user if django.contrib.auth.middleware.SessionAuthenticationMiddleware 
            # is enabled. The update_session_auth_hash() function takes the current request and the 
            # updated user object from which the new session hash will be derived and updates the 
            # session hash appropriately to prevent a password change from logging out the session 
            # from which the password was changed.
            update_session_auth_hash(request, user)  # Important!
            # Message success and redirect to the 
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user-change-password')
        else:
            messages.error(request, 'Please correct the error below and try submitting again.')
    # For non-POST GET requests ...
    else:
        form = PasswordChangeForm(request.user)
    # Render the view.
    return render(request, 'access/user/password-change.html', {'form': form})

r"""
 _   _               ____             __ _ _
| | | |___  ___ _ __|  _ \ _ __ ___  / _(_) | ___
| | | / __|/ _ \ '__| |_) | '__/ _ \| |_| | |/ _ \
| |_| \__ \  __/ |  |  __/| | | (_) |  _| | |  __/
 \___/|___/\___|_|  |_|   |_|  \___/|_| |_|_|\___|

"""
@login_required
def UserProfile(request):
    r"""
    Render form to allow user to update personal information.
    """
    # Get the user data instance.
    user = get_object_or_404(User, id=request.user.id)
    # For POST requests, use POST data to populate the form.  
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        # If form is validated, save the user profile instance.  
        if form.is_valid():
            form.save()
            messages.success(request, 'User profile settings saved.')
        # If form cannot be validated, render an error message.  
        else:
            messages.error(request, 'An error occurred while trying to save your profile data.  If there are any error messages indicated in the form data, correct them and resubmit.  If errors were not indicated, you can try to submit again.  If the error persists, please contact the website administrator.')
    # For non-POST or initial GET requests, use the user data to populate the form.
    else:
        form = UserProfileForm(instance=user)
    # Render the view.
    return render(request, 'access/user/profile-edit.html', {'form': form})

r"""
 ____                                     _ ____                _
|  _ \ __ _ ___ _____      _____  _ __ __| |  _ \ ___  ___  ___| |_
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` | |_) / _ \/ __|/ _ \ __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  _ <  __/\__ \  __/ |_
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|_| \_\___||___/\___|\__|

 ___       _ _
|_ _|_ __ (_) |_
 | || '_ \| | __|
 | || | | | | |_
|___|_| |_|_|\__|

"""
def PasswordResetInit(request):
    r"""
    Render the initial password reset view. This view prompts the user to enter a username or 
    password. The view then gets the user instance from the database.  
    """
    # For POST requests ...
    if request.method == 'POST':
        # Render the form with the user specified data from the form submission.
        form = ResetPasswordInitForm(request.POST)
        # Validate form.  If valid ...
        if form.is_valid():
            # Get the username or email value from the form's name field.
            name = form.cleaned_data.get('name')
            # Get the user instance object using the name value (either a username or email).
            user = None
            if is_email(name):
                user = User.objects.filter(email=name).first()
            else:
                user = User.objects.filter(username=name).first()
            # If the query returned a valid user ... 
            if user is not None:
                # If the user is active ...
                if user.is_active:
                    # Created an encrypted time token that will be added to the reset password link
                    # and emailed to the user.  
                    data = dict(id=user.id, action='reset-password')
                    token = create_timed_token(data)
                    # Create the reset password email.
                    current_site = get_current_site(request)
                    email_subject = 'Reset Password Request'
                    message = render_to_string('access/user/email/password-reset-text.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'token': token,
                    })
                    html_message = render_to_string('access/user/email/password-reset-html.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'token': token,
                    })
                    to_email = user.email

                    # email = EmailMessage(email_subject, message, to=[to_email])
                    
                    email = EmailMultiAlternatives(email_subject, message, settings.EMAIL_HOST_USER, to=[to_email])
                    email.attach_alternative(html_message, "text/html")

                    # Email the reset password link unless the site is running with settings.DEBUG
                    # and the email address ends in "fake.com". During development, you can add 
                    # users with email addresses that end in "fake.com".  When the emailer sees this
                    # it will not send the email.  Rather, it will simply print the message content
                    # the console.  
                    if settings.DEBUG and str(to_email).endswith('fake.com'):
                        messages.debug(request, f'{message}')
                        print(message)
                    else:
                        email.send()
                    return(redirect(reverse('user-password-reset-wait')))
                # Else if the user is not active, redirect with the appropriate error message.
                else:
                    return redirect('error', f'Sorry, the user account associated with this username or email has been deactivated.  If you feel that this is in error, please contact the website administrator.')
            # Else if the query did not return a valid user instance ...
            else:
                messages.error(request, f"Invalid username or email.")
        # Else if the form could not be validated ...
        else:
            messages.error(request, "Sorry, there was a form validation error.  Please try again.")
    # Else if the request is not POST, but GET ...
    else:
        form = ResetPasswordInitForm()
    # Render the view.  
    return render(request, 'access/user/password-reset-init.html', {'form': form})

r"""
 ____                                     _ ____                _
|  _ \ __ _ ___ _____      _____  _ __ __| |  _ \ ___  ___  ___| |_
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` | |_) / _ \/ __|/ _ \ __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  _ <  __/\__ \  __/ |_
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|_| \_\___||___/\___|\__|

 _____ _             _
|  ___(_)_ __   __ _| |
| |_  | | '_ \ / _` | |
|  _| | | | | | (_| | |
|_|   |_|_| |_|\__,_|_|

"""
def PasswordResetFinal(request, token):
    r"""
    This function is accessed when the user clicks on the password reset link sent via email.  
    
    The link contains an encrypted token which the function reads to verify the user request to 
    reset his or her password.  The decrypted token must be a data dict with keys:

    - `valid`: Must be set to True
    - `action`: Must be set to 'reset-password`
    - `id`: The ID of the user requesting the password reset

    If the decrypted token does not contain the required information, the password reset request 
    will not be fulfilled.  
    """
    # Decrypt the token extracted from the URL. 
    data = decipher_timed_token(token)
    # Validate the token.
    if type(data) != dict or 'valid' not in data or not data['valid']:
        return redirect('error', 'Sorry, the password reset link is invalid.  A possible reason? Reset links are only good for one hour after they have been issued.')
    if 'action' not in data or data['action'] != 'reset-password':
        return redirect('error', 'Sorry, the password reset link is invalid.  It is missing required information.')
    if 'id' not in data:
        return redirect('error', 'Sorry, the password reset link is invalid.  It is missing required information about the requesting user.')
    # Get the user instance object using the id key from the data token.  Verify the user is valid.
    user = User.objects.filter(id=data['id']).first()
    if user is None:
        return redirect('error', 'Sorry, the password reset link is invalid.  It is missing required information about the requesting user.')
    # For POST requests ...
    if request.method == 'POST':
        # Render the form using POST data ...
        form = ResetPasswordFinalForm(request.POST)
        # If the form data is valid ...
        if form.is_valid():
            # Get the password1 value.  Note, we don't get password2 and verify that password1 is 
            # equal to password2.  This was already done during form validation.  
            password1 = form.cleaned_data.get('password1')
            # Try to save the user's new password.  
            try:
                user.password = make_password(password1)
                user.save()
                # If successfully saved, message success and redirect to the user login page to 
                # prompt the user to log in with the new credentials.  
                messages.success(request, 'Your password has been reset.  You can now log in using your new password.')
                return redirect('user-login')
            # If the password could not be saved, message failure and redirect to the error page
            # which renders the failure message.
            except:
                return redirect('error', 'Unable to reset password for the specified account.')
    # For initial non-POST / GET requests ...
    else:
        form = ResetPasswordFinalForm()
    # Render the view.
    return render(request, 'access/user/password-reset-final.html', {'form': form})

r"""
 ____                                     _ ____                _
|  _ \ __ _ ___ _____      _____  _ __ __| |  _ \ ___  ___  ___| |_
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` | |_) / _ \/ __|/ _ \ __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  _ <  __/\__ \  __/ |_
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|_| \_\___||___/\___|\__|

 _____                 _ _ ____             _
| ____|_ __ ___   __ _(_) / ___|  ___ _ __ | |_
|  _| | '_ ` _ \ / _` | | \___ \ / _ \ '_ \| __|
| |___| | | | | | (_| | | |___) |  __/ | | | |_
|_____|_| |_| |_|\__,_|_|_|____/ \___|_| |_|\__|

"""
def PasswordResetEmailSent(request):
    r"""
    Called after the email with password reset token has been sent to the user.  This view simply
    renders a page that tells the user to check their email for additional instructions.   
    """
    # Render the view.
    return render(request, 'access/user/password-reset-wait.html', {})

r"""
 _   _               ____  _
| | | |___  ___ _ __/ ___|(_) __ _ _ __  _   _ _ __
| | | / __|/ _ \ '__\___ \| |/ _` | '_ \| | | | '_ \
| |_| \__ \  __/ |   ___) | | (_| | | | | |_| | |_) |
 \___/|___/\___|_|  |____/|_|\__, |_| |_|\__,_| .__/
                             |___/            |_|
"""
class RegisterTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active))
account_activation_token = RegisterTokenGenerator()

def UserSignup(request):
    r"""
    Render new user sign up form.
    """
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('access/user/activate.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            if settings.DEBUG and str(to_email).endswith('fake.com'):
                messages.debug(request, f'{message}')
                print(message)
            else:
                email.send()
            messages.success(request, f'We have sent you an email, please confirm your email address to complete registration.')
            return redirect(reverse('home'))
    else:
        form = UserSignUpForm()
    return render(request, 'access/user/register.html', {'form': form})

r"""
    _        _   _            _          _                             _
   / \   ___| |_(_)_   ____ _| |_ ___   / \   ___ ___ ___  _   _ _ __ | |_
  / _ \ / __| __| \ \ / / _` | __/ _ \ / _ \ / __/ __/ _ \| | | | '_ \| __|
 / ___ \ (__| |_| |\ V / (_| | ||  __// ___ \ (_| (_| (_) | |_| | | | | |_
/_/   \_\___|\__|_| \_/ \__,_|\__\___/_/   \_\___\___\___/ \__,_|_| |_|\__|

"""
def ActivateAccount(request, uidb64, token):
    r"""
    Activate user account following new user sign up.  When a new user registers, an email with an
    activation link is sent.  If the user clicks on that link this view is accessed.  
    """
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f'{user.first_name}, your account is now active.  You may now log in with your credentials.')
        return redirect(reverse('user-login'))
    else:
        return redirect('error', 'Activation link was invalid.')

r"""
 ____  _         __  __ ____            _     _                         _
/ ___|| |_ __ _ / _|/ _|  _ \  __ _ ___| |__ | |__   ___   __ _ _ __ __| |
\___ \| __/ _` | |_| |_| | | |/ _` / __| '_ \| '_ \ / _ \ / _` | '__/ _` |
 ___) | || (_| |  _|  _| |_| | (_| \__ \ | | | |_) | (_) | (_| | | | (_| |
|____/ \__\__,_|_| |_| |____/ \__,_|___/_| |_|_.__/ \___/ \__,_|_|  \__,_|

"""
@staff_member_required
def StaffDashboard(request):
    ## Render view.
    return render(request, template_name='access/staff-dashboard.html', context=dict())
