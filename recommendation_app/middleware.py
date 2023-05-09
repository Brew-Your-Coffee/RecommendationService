from django.http import HttpResponseForbidden

from RecommendationService.settings import ALLOWED_MIDDLEWARE_IPS


class IPFilterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.META)
        if request.path == 'reset/':
            allowed_ips = ALLOWED_MIDDLEWARE_IPS

            user_ip = request.META.get('REMOTE_ADDR')

            if user_ip not in allowed_ips:
                return HttpResponseForbidden('Access Forbidden')

        response = self.get_response(request)
        return response
