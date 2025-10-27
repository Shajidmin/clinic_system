from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Run makemigrations and migrate. Use --reset to remove sqlite DB and run fresh (destructive)."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete sqlite DB and run migrations fresh (destructive).')
        parser.add_argument('--apps', nargs='*', help='Optional list of apps to makemigrations for (default: all).')
        parser.add_argument('--clear-data', action='store_true', help='Delete all Appointment/Doctor/Patient records and non-superuser Users (destructive).')

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        apps = options.get('apps') or []
        clear = options.get('clear_data', False)

        db_path = None
        try:
            base = settings.BASE_DIR
            db_path = os.path.join(str(base), 'db.sqlite3')
        except Exception:
            db_path = os.path.join(os.getcwd(), 'db.sqlite3')

        if clear:
            # perform destructive clear of application data but keep superusers
            self.stdout.write(self.style.WARNING("Clearing application data (Appointments/Doctors/Patients and non-superuser Users)..."))
            try:
                # import models lazily (Django setup already done when running management command)
                from appointments.models import Appointment, Doctor, Patient
                from django.contrib.auth import get_user_model
                User = get_user_model()

                Appointment.objects.all().delete()
                Doctor.objects.all().delete()
                Patient.objects.all().delete()
                # delete users except superusers/staff if you prefer to keep staff change the filter
                deleted_count, _ = User.objects.filter(is_superuser=False).delete()
                self.stdout.write(self.style.SUCCESS(f"Cleared data. Deleted non-superuser Users and related records. ({deleted_count} user records removed)"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR("Failed to clear data:"))
                self.stdout.write(str(exc))
                return

            # After clearing data we can exit or continue to migrations as desired.
            # We'll continue to run migrations below unless --reset was set.
            if not reset:
                self.stdout.write(self.style.NOTICE("Data cleared. Proceeding with migrations..."))

        if reset:
            if os.path.exists(db_path):
                self.stdout.write(self.style.WARNING(f"Removing SQLite DB at {db_path} (destructive)."))
                os.remove(db_path)
            else:
                self.stdout.write(self.style.NOTICE(f"No sqlite DB found at {db_path}."))

            # Optionally clean migrations folders? (NOT removing to avoid data loss)
            self.stdout.write(self.style.NOTICE("Reset performed. Proceeding with makemigrations/migrate."))

        try:
            if apps:
                self.stdout.write(self.style.NOTICE(f"Making migrations for apps: {', '.join(apps)}"))
                call_command('makemigrations', *apps)
            else:
                self.stdout.write(self.style.NOTICE("Making migrations for all apps..."))
                call_command('makemigrations')

            self.stdout.write(self.style.NOTICE("Applying migrations..."))
            call_command('migrate')
        except Exception as exc:
            self.stdout.write(self.style.ERROR("Migration failed:"))
            self.stdout.write(str(exc))
            self.stdout.write(self.style.ERROR("If you changed AUTH_USER_MODEL after migrating, consider resetting DB (destructive):"))
            self.stdout.write(self.style.ERROR("  - Stop server"))
            self.stdout.write(self.style.ERROR(f"  - Run: python manage.py ensure_db --reset"))
            return

        self.stdout.write(self.style.SUCCESS("Migrations applied successfully."))
        self.stdout.write(self.style.SUCCESS("Now create a superuser (python manage.py createsuperuser) or run create_sample_data."))

