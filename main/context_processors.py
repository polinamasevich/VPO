from django.conf import settings

def global_settings(request):
    return {
        'TIME_ZONE': settings.TIME_ZONE,
    }