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
            
            username = email
            if len(username) > 30:
                username = username.split('@')[0]
            if not f_name and not l_name:
                f_name = username

            existing_users = User.objects.filter(email=email)
            if len(existing_users) == 1:
                print "Note: %s exists in User table, updating details" % email
                user = existing_users[0]
                user.first_name = user.first_name or f_name
                user.last_name = user.last_name or l_name
                user.save()
                if not Candidate.objects.filter(user=user).exists():
                    candidate = Candidate(user=user, ssn=ssn, election=election)
                    candidate.save()
                print email, "updated"

            elif len(existing_users) == 0:
                user = User(username=username, first_name=f_name, last_name=l_name, email=email)
                user.set_unusable_password()
                user.save()
                candidate = Candidate(user=user, ssn=ssn, election=election)
                candidate.save()
                print email, "created"

            else:
                print "Note: %s is ambiguous, skipping" % email
                continue
