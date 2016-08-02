"""vaa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView

from vaa.questions import views as vaav
from vaa.staticpages import views as vaas

urlpatterns = [
    url(r'^userpage/$', vaav.userpage),
    url(r'^$', vaav.home),
    url(r'^userupdate/', vaav.userupdate),
    url(r'^candans/(?P<election>[\w\d]+)/$', vaav.candanswer),
    url(r'^candanswer/(?P<election>[\w\d]+)/$', vaav.candreply),
    url(r'^voterform/(?P<election>[\w\d]+)/$', vaav.voterform),
    url(r'^voterform/(?P<election>[\w\d]+)/(?P<hashcode>[\w\d]+)/$', vaav.voterform),
    url(r'^compare/(?P<election>[\w\d]+)/$', vaav.compare),
    url(r'^compare/(?P<election>[\w\d]+)/(?P<hashcode>[\w\d]+)/$', vaav.compare_load),
    url(r'^oldanswers/(?P<election>[\w\d]+)/$', vaav.oldanswers),
    url(r'^candidate/(?P<pk>\d+)/$', vaav.candidate_page),

    #url(r'^candidate/(?P<pk>\d+)/', vaav.candidate_page),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', { 'extra_context':{'next':'/userpage/'}}),
    url(r'^accounts/profile/$', RedirectView.as_view(url="/userpage/")),
    url(r'^admin/', admin.site.urls),
    url(r'^absents/(?P<election>[\w\d]+)/$', vaav.absents),
    url(r'^clearsession/', vaav.clear_session),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + [
    url(r'^page/(?P<slug>[\w\d_-]+)', vaas.page),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
