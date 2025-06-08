from django.contrib import admin

from .models import Article
from .forms import ArticleAdminForm

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    fieldsets = (
        ('Title', {
            'fields': ['title', 'slug'],
        }),
        ('Article', {
            'fields': ['content'],
        }),
        ('Miscellaneous', {
            'fields': ['priority', 'featured', 'active'],
        }),
    )
    list_display = ['title', 'slug', 'priority', 'featured', 'active']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['active', 'featured']
    search_fields = ['title', 'content']
    ordering = ['priority']
    list_editable = ['priority', 'featured', 'active']