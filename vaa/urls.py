from django.conf.urls import include, url

urlpatterns = [
    url(r'^[\w_]+/', include('vaa.questions.urls'))
]
