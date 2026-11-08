# Back-end-Development-Capstone

Django website integrating the band's Pictures and Songs microservices.

## Features
Home, Songs with a lyrics modal, Photos, sign-up, login/logout, and Concerts.
Authenticated visitors choose their attendance status. Each user updates only their
own attendance. Django Admin manages concerts. Passwords use Django's password hashing.
REST requests have timeouts and return a 503 page if a service is unavailable.

## Configuration
`PICTURES_SERVICE` and `SONGS_SERVICE` are the base URLs of the two Flask services.
`DJANGO_ALLOWED_HOSTS` is a comma-separated list of approved hostnames.
Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=0` for an external deployment.
An admin is created on container startup only when both `DJANGO_SUPERUSER_USERNAME`
and `DJANGO_SUPERUSER_PASSWORD` are explicitly provided.

## Run and test
```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test -v 2
python manage.py runserver 0.0.0.0:8000
```
The initial migration has been generated and applied successfully. Seven tests pass,
including registration, duplicate usernames, login/logout, attendance isolation,
missing concerts, service response rendering, and service outages.

## Create an administrator and use the application
After installing requirements and running migrations, run:
```sh
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```
Choose a username and password interactively; do not commit credentials. Open
`http://localhost:8000/admin/` and sign in with the administrator account to add
concert records. The same `/admin/` path is available on the deployed application.
For a container, run `python manage.py createsuperuser` inside the running Django
container, or provide the documented superuser environment variables at startup.

Open `/` for the band home page, `/songs` for the song list and Lyrics dialogs,
and `/photos` for photos. Register a listener through Sign Up, log in, open
Concerts, and select a concert to record attendance. Log Out ends the session.
The Songs service returns an object containing a `songs` list; the Django adapter
also accepts the earlier bare-list response during a staged service upgrade.

## Container deployment
```sh
docker build -t djangoserver:1 .
docker run --rm -p 8000:8000 --env PICTURES_SERVICE --env SONGS_SERVICE --env DJANGO_SECRET_KEY djangoserver:1
```
WhiteNoise serves the collected static assets. Migrations run on container startup.
SQLite is suitable for this single-replica teaching deployment. Database contents
are excluded from the repository and container build context.

## Environment Setup
The project starts from the IBM Skills Network course template, retaining its license.
The original `bin/setup.sh` describes the Linux lab setup. For the current environment,
create a virtual environment and install `requirements.txt`. Containers use Python 3.9.16.
Local validation used Python 3.12. Cloud IDE provides Python 3.10.12.
Do not commit `.env`, database files, generated users, or registry credentials.
