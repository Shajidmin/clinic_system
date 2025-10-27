from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Run makemigrations, migrate, and create a superuser (supports env vars or options)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=os.environ.get('DJANGO_SUPERUSER_USERNAME'),
                            help='Superuser username (or set DJANGO_SUPERUSER_USERNAME)')
        parser.add_argument('--email', default=os.environ.get('DJANGO_SUPERUSER_EMAIL'),
                            help='Superuser email (or set DJANGO_SUPERUSER_EMAIL)')
        parser.add_argument('--password', default=os.environ.get('DJANGO_SUPERUSER_PASSWORD'),
                            help='Superuser password (or set DJANGO_SUPERUSER_PASSWORD)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Making migrations for all apps...'))
        call_command('makemigrations')
        self.stdout.write(self.style.NOTICE('Applying migrations...'))
        call_command('migrate')

        User = get_user_model()
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@example.com'
        password = options.get('password')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
            return

        if not password:
            # No password provided: fall back to interactive createsuperuser (will prompt)
            self.stdout.write(self.style.WARNING(
                'No password provided via --password or DJANGO_SUPERUSER_PASSWORD; '
                'falling back to interactive createsuperuser.'))
            call_command('createsuperuser', username=username, email=email)
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
