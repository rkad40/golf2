from django.db import models

# Create your models here.

r"""
"""

class Article(models.Model):
    title = models.CharField('Title', max_length=200, unique=False)
    slug = models.SlugField('Slug', max_length=200, unique=True, null=False, help_text="A slug is unique name reference for the page.  Once created, do not change the slug -- not unless all page references that use it are also changed.")
    content = models.TextField('Content', help_text="Remainder of the article content.")
    priority = models.IntegerField('Priority', unique=False, default=50, null=False, blank=False, help_text="Priority order (where 1 is the highest priority).")
    featured = models.BooleanField('Featured', default=False, help_text="Make a featured article?")
    active = models.BooleanField('Active', default=True)
    def __str__(self):
        return f'Article: "{self.title}"'
        
 

