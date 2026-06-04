from django.conf import settings


def show_debug_toolbar(request):
    if not settings.DEBUG:
        return False

    if request.path_info.startswith("/summernote/editor/"):
        return False

    return request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS
