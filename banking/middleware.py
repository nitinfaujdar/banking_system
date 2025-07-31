import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.timezone:
            tz = user.profile.timezone or 'UTC'
            try:
                timezone.activate(pytz.timezone(tz))
            except pytz.UnknownTimeZoneError:
                timezone.activate(pytz.UTC)
        else:
            timezone.deactivate()