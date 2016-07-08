from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

from vaa.utils import trunc, zipvalues

def simple_distance(this, other):
    other_mul = other[1]
    other = other[0]
    this = int(this)
    if this == 6 or other == 6:
        return 1 * other_mul
    else:
        return (max(this, other) - min(this, other)) * other_mul

class Candidate(models.Model):
    user = models.ForeignKey(User)
    ssn = models.CharField(max_length=11)
    picture = models.ImageField(null=True, blank=True)
    blurb = models.TextField()

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def last_answers(self):
        return self.answersheet_set.order_by('-timestamp').first().answers

    def compare(self, other_data, method=simple_distance):
        d = zipvalues(other_data, d=True)
        return sum([method(value, d[key]) for key, value in self.last_answers if 'q_' in key])

    def name(self):
        return self.user.get_full_name()


class Question(models.Model):
    order = models.IntegerField()
    active = models.BooleanField()

    def __unicode__(self):
        istext = self.questiontext_set.get(lang="IS")
        return trunc(istext.text, 30)


class QuestionText(models.Model):
    lang = models.CharField(max_length=2)
    text = models.TextField()
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return trunc(self.text, 30)

class AnswerText(models.Model):
    lang = models.CharField(max_length=2)
    text = models.TextField()
    mod = models.IntegerField()

    def __unicode__(self):
        return self.text + ":" + unicode(self.mod)


class AnswerSheet(models.Model):
    timestamp = models.DateTimeField()
    candidate = models.ForeignKey(Candidate, null=True, blank=True)
    answers = JSONField()

    def __unicode__(self):
        return self.candidate.user.get_full_name()
