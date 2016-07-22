from django.contrib import admin
from django.core.cache import cache

from .models import Page

def reset_cache(pattern):
    keys = cache.keys(pattern)
    for key in keys:
        cache.delete(key)

class PageAdmin(admin.ModelAdmin):
    def delete_model(request, obj):
        reset_cache("*")
        super(PageAdmin, self).delete_model(request, obj)

    def save_model(self, request, obj, form, change):
        reset_cache("*")
        super(PageAdmin, self).save_model(request, obj, form, change)


admin.site.register(Page, PageAdmin)


