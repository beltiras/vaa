from django.contrib import admin

from .models import Candidate, Question, QuestionText, AnswerSheet, AnswerText


class QuestionTextInline(admin.TabularInline):
    model = QuestionText


class AnswerSheetInline(admin.TabularInline):
    model = AnswerSheet


class CandidateAdmin(admin.ModelAdmin):
    inlines = [AnswerSheetInline,]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionTextInline,]


class AnswerSheetAdmin(admin.ModelAdmin):
    pass


class AnswerTextAdmin(admin.ModelAdmin):
    pass

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AnswerSheet, AnswerSheetAdmin)
admin.site.register(AnswerText, AnswerTextAdmin)
