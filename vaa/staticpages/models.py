# encoding=utf8
from django.db import models

import markdown

class Page(models.Model):
    TEXT_TYPES = (
        ('M', 'Markdown'),
        ('H', 'HTML')
    )
    extra_head = models.TextField(u"Aukahlutir í HEAD tag", null=True, blank=True)
    text_type = models.CharField(u"Tegund texta", max_length=1, choices=TEXT_TYPES)
    page_url = models.SlugField(u"URL sem síðan á að vera á", max_length=64, db_index=True)
    text = models.TextField()
    menubar = models.CharField(u"Texti í anchor", max_length=64)
    place_in_menubar = models.BooleanField(u"Setja þessa síðu í síðuhaus")
    order_in_menubar = models.IntegerField(u"Röð í síðuhaus", unique=True, db_index=True)

    def render(self):
        if self.text_type == 'H':
            return self.text
        else:
            return markdown.markdown(self.text)

    @property
    def head_related(self):
        return {
            'page_url':self.page_url,
            'menubar':self.menubar,
        }
