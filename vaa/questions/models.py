from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

from vaa.utils import trunc, zipvalues

def simple_distance(this, other):
    other_mul = other[1]
    other = other[0]
    this = int(this)
    if this == 6 or other == 6:
        return settings.INDECISION_PARAMETER * other_mul
    else:
        return (max(this, other) - min(this, other)) * other_mul

class Election(models.Model):
    ends = models.DateTimeField() # Time after which new answers from candidates will not be accepted
    slug = models.CharField(max_length=64) # URL access, pref. something like reykjavik2016 or nordvest2016

    def __unicode__(self):
        return self.slug


class Question(models.Model):
    order = models.IntegerField()
    active = models.BooleanField()
    election = models.ForeignKey(Election)

    def __unicode__(self):
        istext = self.questiontext_set.get(lang="IS")
        return trunc(istext.text, 30)

    def get_text(self, lang="IS"):
        return self.questiontext_set.get(lang=lang)


class Candidate(models.Model):
    user = models.ForeignKey(User)
    ssn = models.CharField(max_length=11)
    picture = models.ImageField(
        null=True,
        blank=True,
        upload_to=settings.MEDIA_UPLOADS + 'cand_pics'
    )
    blurb = models.TextField()
    election = models.ForeignKey(Election)


    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def last_answers(self):
        a = self.answersheet_set.order_by('-timestamp').first()
        if a:
            return a.answers
        return None

    def compare(self, other_data, method=simple_distance):
        q_pk = [q.pk for q in Question.objects.filter(active=True, election=self.election)]
        d = dict(zipvalues(other_data, q_pk, d=True))
        print "model.compare",d
        la = dict(self.last_answers)
        if not la:
            la = dict([('q_%s' % q_pk, 6) for pk in q_pk])
        return sum([method(la.get('q_%s' % pk, 6), d.get('q_%s' % pk, (3,6))) for pk in q_pk])

    def name(self):
        return self.user.get_full_name()


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
