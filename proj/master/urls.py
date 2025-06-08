from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from maven.views import ExplorerAdminRoot

urlpatterns = [
    path('', include('access.urls')),
    path('admin/maven/mediaexplorer/', ExplorerAdminRoot, name='maven-explorer-admin'),
    path('admin/maven/mediaexplorer/add/', ExplorerAdminRoot, name='maven-explorer-admin-add'),
    path('maven/', include('maven.urls')), 
    path('', include('main.urls')),
    path('', include('book.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('admin/', admin.site.urls),
]
if settings.DEBUG: # pragma: no cover
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),] + urlpatterns
