from django import forms
from django.forms import ModelForm
from django_summernote.widgets import SummernoteWidget

from .models import Article

class ArticleAdminForm(ModelForm):
    class Meta:
        widgets = {
            'intro': SummernoteWidget(),
            'content': SummernoteWidget(),
        }

