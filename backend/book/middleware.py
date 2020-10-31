from django.http import HttpResponsePermanentRedirect


class DomainRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "futurecoder.herokuapp.com" == request.get_host():
            return HttpResponsePermanentRedirect(
                "https://futurecoder.io" + request.path
            )
        else:
            return self.get_response(request)
