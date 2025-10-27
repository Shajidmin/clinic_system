from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Doctor, Patient, Appointment

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_staff', 'is_superuser')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')
    search_fields = ('user__username', 'specialization')
    list_filter = ('specialization',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'contact')
    search_fields = ('user__username',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_date', 'time_slot', 'doctor', 'patient', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('doctor__user__username', 'patient__user__username')
    ordering = ('-appointment_date', 'time_slot')
