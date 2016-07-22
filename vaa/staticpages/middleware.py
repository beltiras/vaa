import cPickle as pickle

from django.core.cache import cache

from .models import Page


class StaticPageMW:
    def process_request(self, request):
        pages = cache.get("static_page_head", None)
        if not pages:
            pages = [p.head_related for p in Page.objects.filter(place_in_menubar=True).order_by('order_in_menubar')]
            cache.set("static_page_head", pickle.dumps(pages))
        else:
            pages = pickle.loads(pages)
        request.heads = pages
