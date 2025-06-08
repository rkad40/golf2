from django.contrib import admin
from .models import MediaFile, MediaFolder, MediaFolderPolicy, MediaExplorer

@admin.register(MediaExplorer)
class MediaExplorerAdmin(admin.ModelAdmin):
    list_display_links = None

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'created_on', 'created_by', 'is_active']
    list_display_links = ['id', 'url']
    ordering = ['url']
    fields = ['name', 'url', 'created_by', 'updated_by', 'updated_on', 'is_active', 'notes']
    readonly_fields = ['name', 'url']

@admin.register(MediaFolder)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'created_on', 'created_by', 'is_active']
    list_display_links = ['id', 'url']
    ordering = ['url']
    fields = ['name', 'url', 'hint', 'policy', 'created_by', 'is_active', 'notes']
    readonly_fields = ['name', 'url', 'ancestor_folders', 'child_folders']

@admin.register(MediaFolderPolicy)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    ordering = ['name']