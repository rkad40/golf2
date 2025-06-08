from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import PHONE_SERVICE_WITH_BLANK, User

from rex import Rex

r"""
 _   _               _                _       _____
| | | |___  ___ _ __| |    ___   __ _(_)_ __ |  ___|__  _ __ _ __ ___
| | | / __|/ _ \ '__| |   / _ \ / _` | | '_ \| |_ / _ \| '__| '_ ` _ \
| |_| \__ \  __/ |  | |__| (_) | (_| | | | | |  _| (_) | |  | | | | | |
 \___/|___/\___|_|  |_____\___/ \__, |_|_| |_|_|  \___/|_|  |_| |_| |_|
                                |___/
"""
class UserLoginForm(forms.Form):
    r"""
    Render user login form.  
    """
    name = forms.CharField(label='Username or Email', max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    next_url = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        fields = ('name', 'password', 'next_url')

r"""
 _   _               ____             __ _ _      _____
| | | |___  ___ _ __|  _ \ _ __ ___  / _(_) | ___|  ___|__  _ __ _ __ ___
| | | / __|/ _ \ '__| |_) | '__/ _ \| |_| | |/ _ \ |_ / _ \| '__| '_ ` _ \
| |_| \__ \  __/ |  |  __/| | | (_) |  _| | |  __/  _| (_) | |  | | | | | |
 \___/|___/\___|_|  |_|   |_|  \___/|_| |_|_|\___|_|  \___/|_|  |_| |_| |_|

"""
class UserProfileForm(ModelForm):    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'provider')

r"""
 _   _               ____  _                         _____
| | | |___  ___ _ __/ ___|(_) __ _ _ __  _   _ _ __ |  ___|__  _ __ _ __ ___
| | | / __|/ _ \ '__\___ \| |/ _` | '_ \| | | | '_ \| |_ / _ \| '__| '_ ` _ \
| |_| \__ \  __/ |   ___) | | (_| | | | | |_| | |_) |  _| (_) | |  | | | | | |
 \___/|___/\___|_|  |____/|_|\__, |_| |_|\__,_| .__/|_|  \___/|_|  |_| |_| |_|
                             |___/            |_|
"""
class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(max_length=100, required=True)
    phone = forms.CharField(max_length=20, required=False)
    provider = forms.ChoiceField(required=False, choices=PHONE_SERVICE_WITH_BLANK)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'provider', 'password1', 'password2')

r"""
 ____                                     _ ____                _
|  _ \ __ _ ___ _____      _____  _ __ __| |  _ \ ___  ___  ___| |_
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` | |_) / _ \/ __|/ _ \ __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  _ <  __/\__ \  __/ |_
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|_| \_\___||___/\___|\__|

 ___       _ _   _____
|_ _|_ __ (_) |_|  ___|__  _ __ _ __ ___
 | || '_ \| | __| |_ / _ \| '__| '_ ` _ \
 | || | | | | |_|  _| (_) | |  | | | | | |
|___|_| |_|_|\__|_|  \___/|_|  |_| |_| |_|

"""
class ResetPasswordInitForm(forms.Form):
    name = forms.CharField(label='Username or Email', max_length=150, required=True)
    class Meta:
        fields = ('name')

r"""
 ____                                     _ ____                _
|  _ \ __ _ ___ _____      _____  _ __ __| |  _ \ ___  ___  ___| |_
| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` | |_) / _ \/ __|/ _ \ __|
|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  _ <  __/\__ \  __/ |_
|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|_| \_\___||___/\___|\__|

 _____ _             _ _____
|  ___(_)_ __   __ _| |  ___|__  _ __ _ __ ___
| |_  | | '_ \ / _` | | |_ / _ \| '__| '_ ` _ \
|  _| | | | | | (_| | |  _| (_) | |  | | | | | |
|_|   |_|_| |_|\__,_|_|_|  \___/|_|  |_| |_| |_|

"""
class ResetPasswordFinalForm(forms.Form):
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput, required=True)
    class Meta:
        fields = ('password1', 'password2')

    def clean_password1(self):
        value = self.cleaned_data['password1']
        rex = Rex()
        if len(value) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if rex.m(value, r'^\d+$'):
            raise forms.ValidationError("Password must contain non-numeric characters.")
        return(value)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError(f"Passwords do not match ('{password1}' does not match '{password2}').")