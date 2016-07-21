import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from vaa.questions.models import Candidate, Election


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
        try:
            election = Election.objects.get(slug=options['election'])
        except:
            raise CommandError("Is the election " + options['election'] + " in the database?")

        data = csv.reader(datafile)
        for row in data:
            f_name, l_name, ssn, email = row
            
            if len(User.objects.filter(email=email)):
                print "%s exists in User table, skipping %s" % (email, row)
                continue
            user = User(username=email, first_name=f_name, last_name=l_name, email=email)
            user.set_unusable_password()
            user.save()
            candidate = Candidate(user=user, ssn=ssn, claimed=False, election=election)
            candidate.save()
            print email, "created"
