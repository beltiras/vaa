import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from vaa.questions.models import Question, QuestionText, Election
from vaa.utils import randstring


class Command(BaseCommand):
    help = 'Import CSV data from a file and enter into Candidate table'

    def add_arguments(self, parser):
        parser.add_argument('file', type=unicode)
        parser.add_argument('election', type=unicode)

    def handle(self, *args, **options):
        try:
            datafile = open(options['file'], mode="rb+")
        except IOError:
            raise CommandError('IOError, does %s exist?' % options['file'][0])
        data = csv.DictReader(datafile)
        count = 0
        try:
            election = Election.objects.get(slug=options['election'])
        except:
            raise CommandError("Is the election " + options['election'] + " in the database?")
        for row in data:
            active = row.pop("Active")
            order = row.pop("Order")
            question = Question(active=active, order=order, election=election)
            question.save()
            for lang in row:
                qt = QuestionText(lang=lang, text=row[lang], question=question)
                qt.save()
            count += 1
        print "Added",count,"questions"
