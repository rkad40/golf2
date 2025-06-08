from maven.widgets import MavenFileSelectorAdminWidget, MavenImageSelectorAdminWidget, MavenDirSelectorAdminWidget
from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import Course, Tournament, Player

# class EmailContactForm(forms.Form):
#     email_to = forms.ModelChoiceField(label='To', queryset=Contact.objects.filter(active=True,email__isnull=False).all(), to_field_name='name', required=True)
#     email_from = forms.EmailField(label='From', required=True, max_length=200, help_text="Please make sure your email address is correct.  Otherwise you will not get the recipient's reply.")
#     subject = forms.CharField(label='Subject', required=True, max_length=200)
#     message = forms.CharField(label='Message', required=True, widget=forms.Textarea(attrs={'width':"100%", 'rows': "6"}))
#     class Meta:
#         fields = ['email_to', 'email_from', 'subject', 'message']

class ScoreCardForm(forms.Form):
    data = forms.CharField(widget=forms.HiddenInput())

DATA_TYPE_CHOICES = [
    ('json', 'JSON data'),
    # ('yaml', 'YAML'),
    # ('csv', 'CSV'),
    ('tab', 'TAB delimited data (copy-pasted from a spreadsheet)'),
]

DATA_TABLE_CHOICES = [
    ('Team', 'Teams'),
    ('Hole', 'Holes (if selected, must choose Course below)'),
]

DATA_ACTION_CHOICES = [
    ('merge', 'Try to merge'),
    ('overwrite', 'Overwrite existing data'),
]

class CreateTableForm(forms.Form):
    table = forms.ChoiceField(
        label='Table',
        required=True,
        choices = DATA_TABLE_CHOICES,
        help_text='Select the table data type to be created.  NOTE: If the table already exists, it will be overwritten.'
    )
    course = forms.ChoiceField(
        label='Course',
        required=False,
        choices = [(course.id, str(course)) for course in Course.objects.filter(active=True)],
        help_text='Only required if editing the holes table for a specific course.'
    )
    data = forms.CharField(
        label='Raw Data',
        required=True,
        max_length=100000, 
        widget=forms.Textarea(attrs={"rows":5, "cols":20}),
        help_text='Copy-paste data into text area.',
    )
    data_type = forms.ChoiceField(
        label='Data Type',
        required=True,
        choices = DATA_TYPE_CHOICES,
        help_text='Select the raw data format.',
    )    

class VerifyTableForm(forms.Form):
    table = forms.CharField(
        label='Table',
        required=True,
        widget=forms.HiddenInput(),
        help_text='Select the table data type to be created.  NOTE: If the table already exists, it will be overwritten.'
    )
    course = forms.CharField(
        label='Course',
        required=False,
        widget=forms.HiddenInput(),
        help_text='Only required if editing the holes table for a specific course.'
    )
    data = forms.CharField(
        label='Raw Data',
        required=True,
        max_length=100000, 
        widget=forms.HiddenInput(),
        help_text='Copy-paste data into text area.',
    )
    data_type = forms.CharField(
        label='Data Type',
        required=True,
        widget=forms.HiddenInput(),
        help_text='Select the raw data format.',
    )        

class AdminActionsForm(forms.Form):
    action = forms.CharField(
        label='Action',
        required=False,
        widget=forms.HiddenInput(),
    )

class TeamLoginForm(forms.Form):
    team = forms.CharField(
        label='Team Name',
        required=True,
        help_text="Your team name will be of the form 01A, 17B, etc.  The value is made up of a two-digit number representing your start hole and a letter.  You can omit the leading zero (if there is one).  Also, case does not matter.",
    )
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput(),
        help_text="Enter your team password in the field provided.  Case does not matter.  Then hit <strong>Log In</strong>.",
    )

def past_tournament_choices():
    return [(tournament.id, str(tournament)) for tournament in Tournament.objects.filter(archived=True).order_by('-date_time').all()]
    # return [(tournament.id, str(tournament)) for tournament in Tournament.objects.filter(archived=True)]

class PastTournamentsForm(forms.Form):
    tournament = forms.ChoiceField(
        label='Tournament',
        required=True,
        choices = past_tournament_choices,
        help_text='Choose a past tournament from the list.'
    )

class TournamentAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'archive_notes': SummernoteWidget(),
        }

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'spelling', 'email', 'phone', 'handicap', 'score', 'vote', 'comment']
        widgets = {
            'name': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 5}),
        }        