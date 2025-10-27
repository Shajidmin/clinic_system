from django.shortcuts import render
from django.db.utils import OperationalError

class DatabaseAvailabilityMiddleware:
    """
    Catch OperationalError (e.g. 'no such table') and show a friendly page
    with instructions to initialize/reset the DB instead of crashing.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except OperationalError as exc:
            # Only handle typical 'no such table' errors to avoid hiding other db issues
            msg = str(exc)
            if 'no such table' in msg.lower():
                context = {
                    'error_msg': msg,
                    'fix_commands': [
                        "Open cmd in the project folder (where manage.py is)",
                        r"venv\\Scripts\\activate",
                        "python manage.py ensure_db",
                        "or (destructive) python manage.py ensure_db --reset",
                        "or to clear previous app data: python manage.py ensure_db --clear-data"
                    ],
                    'features': [
                        ("Fast Booking", "Choose doctor, date and time in seconds."),
                        ("Manage Appointments", "Reschedule, confirm, or cancel with clear status updates."),
                        ("Role-based Access", "Separate patient, doctor and admin dashboards."),
                    ]
                }
                return render(request, 'db_unavailable.html', context, status=503)
            # re-raise other OperationalError variants
            raise
