from django.conf import settings

class URLMalformedError(Exception):
    pass

class UrlProtectionMW:
    def process_request(self, request):
        print request.path
        urlparts = request.path.split("/")
        if urlparts[1] != settings.INSTANCE_NAME:
            raise URLMalformedError(urlparts[1]+" is not proper first part of URL")
        request.instance = urlparts[1]
