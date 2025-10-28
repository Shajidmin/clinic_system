from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT,
    )

class Doctor(models.Model):
    DAYS_OF_WEEK = (
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    )

    TIME_SLOTS = (
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100)
    available_days = MultiSelectField(choices=DAYS_OF_WEEK)
    time_slots = MultiSelectField(choices=TIME_SLOTS)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient')
    age = models.PositiveIntegerField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Patient"

class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'BOOKED', 'Booked'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=Doctor.TIME_SLOTS)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'time_slot')
        ordering = ['appointment_date', 'time_slot']

    def __str__(self):
        doctor_name = self.doctor.user.get_full_name() or self.doctor.user.username
        patient_name = self.patient.user.get_full_name() or self.patient.user.username
        return f"{self.appointment_date} {self.time_slot} - Dr. {doctor_name} with {patient_name}"
