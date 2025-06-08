from django.conf import settings
from django.utils.dateparse import parse_datetime
import pytz

def local_datetime(dt):
    tz = pytz.timezone(settings.TIME_ZONE)
    local_dt = dt.astimezone(tz)
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')
