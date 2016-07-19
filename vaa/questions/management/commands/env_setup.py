from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string
from fabric.api import run

from vaa.utils import randstring

class Command(BaseCommand):
    help = 'Create the neccessary infrastructure to run the app (.env, database)'

    def add_arguments(self, parser):
        parser.add_argument('instancename', type=unicode)


    def handle(self, *args, **options):
        instancename = options['instancename']
        password = randstring(32)
        run('psql -U postgres -c "CREATE ROLE %s WITH PASSWORD \'%s\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;' %  (
            instancename,
            password)
            )
        run('CREATE DATABASE %s WITH OWNER=%s ENCODING=\'utf-8\';' % (instancename, instancename))
        envfile = open(settings.BASE_DIR + "/.basenv", "rb+").read()
        
        envfile = envfile.replace(
            "{{ DB_PASS }}", password
        ).replace(
            '{{ SECRET_KEY }}', get_random_string()
        ).replace(
            '{{ INSTANCE_NAME }}', instance_name
            )
        with open(settings.BASE_DIR + ("/.env_%s" % instancename)) as instancenv:
            instancenv.write(envfile)
