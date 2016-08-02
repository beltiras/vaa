#coding=utf8
from django.contrib import admin

from .models import Candidate, Question, QuestionText, AnswerSheet, AnswerText, Election


def send_introductory_email(modeladmin, request, queryset):
    """
    User this to send emails to the candidates to claim their users
    """
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.sites.shortcuts import get_current_site
    from django.core.mail import EmailMultiAlternatives
    from django.template import loader
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    site_info = get_current_site(request)

    for cand in queryset:
        context = {
                'email': cand.user.email,
                'domain': site_info.domain,
                'site_name': site_info.name,
                'uid': urlsafe_base64_encode(force_bytes(cand.user.pk)),
                'user': cand.user,
                'token': default_token_generator.make_token(cand.user),
                'protocol': 'http',
            }
        body = loader.render_to_string("introductory_email.txt", context)
        email_message = EmailMultiAlternatives(
            u"Innskráning í VAA kerfi vegna prófkjörs",
            body,
            'gunnargrims@piratar.is',
            [cand.user.email])
        email_message.send()

send_introductory_email.short_description = u'Senda inngangstölvupóst'


class QuestionTextInline(admin.TabularInline):
    model = QuestionText


class AnswerSheetInline(admin.TabularInline):
    model = AnswerSheet


class CandidateAdmin(admin.ModelAdmin):
    inlines = [AnswerSheetInline,]
    actions = [send_introductory_email,]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionTextInline,]


class AnswerSheetAdmin(admin.ModelAdmin):
    pass


class ElectionAdmin(admin.ModelAdmin):
    pass


class AnswerTextAdmin(admin.ModelAdmin):
    pass

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AnswerSheet, AnswerSheetAdmin)
admin.site.register(AnswerText, AnswerTextAdmin)
admin.site.register(Election, ElectionAdmin)
