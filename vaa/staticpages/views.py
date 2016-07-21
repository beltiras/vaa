from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page

from vaa.utils import render_with

from .models import Page

@cache_page(60*5)
@render_with("static_page.html")
def page(request, slug):
    return {
        'page':get_object_or_404(Page, page_url=slug)
        }
