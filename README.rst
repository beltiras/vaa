=====
Voter Assistance Application
=====
Installation
-----
OS requirements: Postgresql 9.4+, redis-server, Python 2.7, python-virtualenv, psycopg2::

  cd /var/www
  git clone [github_url]
  virtualenv vaa_env
  source vaa_env/bin/activate
  cd vaa
  pip install -r requirements.txt
  sudo su - postgres
  psql
  CREATE DATABASE vaa;
  CREATE ROLE vaa WITH LOGIN PASSWORD 'vaa1234';
  GRANT ALL ON DATABASE vaa TO vaa;
  \q
  exit
  python manage.py migrate
  python manage.py createsuperuser
  # make an election, using shell or Django Admin (yes, there should be a management command for this)
  python manage.py qimport questions.csv [election_slug] # replace with real election slug
  python manage.py cand_import cand.csv [election_slug] # replace with real election slug

Use
-----
There are two management commands of note, qimport and cand_import.  They take csv files as arguments as well as the slug of the election the data are meant for.  cand.csv and questions.csv show the format.  Google docs outputs the proper encoding for latin-1 characters.

To invite candidates to participate, go to /admin/questions/candidate/, select the candidates to invite and select "Senda inngangstölvupóst" from the menu and press Go.
