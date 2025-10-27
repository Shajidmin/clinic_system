from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import Doctor, Patient, Appointment
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Create sample users (admin, doctor, patient) and a sample appointment'

    def handle(self, *args, **options):
        User = get_user_model()

        # Admin
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'AdminPass123'
        admin, created = User.objects.get_or_create(username=admin_username, defaults={
            'email': admin_email,
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {admin_username} / {admin_password}"))
        else:
            self.stdout.write(self.style.NOTICE(f"Superuser '{admin_username}' already exists"))

        # Doctor
        doctor_username = 'drsmith'
        doctor_email = 'drsmith@example.com'
        doctor_password = 'DoctorPass123'
        doctor_user, created = User.objects.get_or_create(username=doctor_username, defaults={
            'email': doctor_email,
            'role': User.Role.DOCTOR,
        })
        if created:
            doctor_user.set_password(doctor_password)
            doctor_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created doctor user: {doctor_username} / {doctor_password}"))
        else:
            # ensure role
            doctor_user.role = User.Role.DOCTOR
            doctor_user.save()
            self.stdout.write(self.style.NOTICE(f"Doctor user '{doctor_username}' already exists"))

        # Doctor profile
        if not hasattr(doctor_user, 'doctor_profile'):
            # pick some availability and slots
            available_days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
            # use first two TIME_SLOTS codes
            time_slots = [code for code, _ in Doctor.TIME_SLOTS][:3]
            Doctor.objects.create(user=doctor_user, specialization='General Practice', available_days=available_days, time_slots=time_slots)
            self.stdout.write(self.style.SUCCESS("Doctor profile created with availability and time slots"))
        else:
            self.stdout.write(self.style.NOTICE("Doctor profile already exists"))

        # Patient
        patient_username = 'alice'
        patient_email = 'alice@example.com'
        patient_password = 'PatientPass123'
        patient_user, created = User.objects.get_or_create(username=patient_username, defaults={
            'email': patient_email,
            'role': User.Role.PATIENT,
        })
        if created:
            patient_user.set_password(patient_password)
            patient_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created patient user: {patient_username} / {patient_password}"))
        else:
            # ensure role
            patient_user.role = User.Role.PATIENT
            patient_user.save()
            self.stdout.write(self.style.NOTICE(f"Patient user '{patient_username}' already exists"))

        # Patient profile
        if not hasattr(patient_user, 'patient'):
            Patient.objects.create(user=patient_user, age=30, gender='F', contact='555-0100')
            self.stdout.write(self.style.SUCCESS("Patient profile created"))
        else:
            self.stdout.write(self.style.NOTICE("Patient profile already exists"))

        # Create a sample appointment for tomorrow using doctor's first available slot
        try:
            doctor_profile = doctor_user.doctor_profile
            patient_profile = patient_user.patient
            # choose tomorrow
            tomorrow = timezone.localdate() + datetime.timedelta(days=1)
            # ensure day code is in doctor availability; find next available day within 7 days
            WEEKDAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
            chosen_date = None
            for delta in range(0, 7):
                d = timezone.localdate() + datetime.timedelta(days=delta)
                if WEEKDAY_MAP[d.weekday()] in doctor_profile.available_days:
                    chosen_date = d
                    break
            if chosen_date is None:
                self.stdout.write(self.style.WARNING("Doctor has no available days configured; skipping sample appointment"))
            else:
                slot = (doctor_profile.time_slots[0] if doctor_profile.time_slots else Doctor.TIME_SLOTS[0][0])
                # avoid duplicate if exists
                exists = Appointment.objects.filter(doctor=doctor_profile, patient=patient_profile, appointment_date=chosen_date, time_slot=slot).exists()
                if not exists:
                    Appointment.objects.create(doctor=doctor_profile, patient=patient_profile, appointment_date=chosen_date, time_slot=slot)
                    self.stdout.write(self.style.SUCCESS(f"Sample appointment created on {chosen_date} at {slot}"))
                else:
                    self.stdout.write(self.style.NOTICE("Sample appointment already exists"))
        except Exception as ex:
            self.stdout.write(self.style.ERROR(f"Could not create sample appointment: {ex}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Sample data creation complete."))
        self.stdout.write("Log in with:")
        self.stdout.write(f" Admin  -> {admin_username} / {admin_password}")
        self.stdout.write(f" Doctor -> {doctor_username} / {doctor_password}")
        self.stdout.write(f" Patient-> {patient_username} / {patient_password}")
        self.stdout.write("")
        self.stdout.write("Then run the server and test booking/rescheduling/cancelling via the dashboards or /admin/.")
