from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.db import IntegrityError
import datetime
from .models import Patient, Doctor, Appointment
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    def get_success_url(self):
        user = self.request.user
        if user.role == user.Role.PATIENT:
            return '/dashboard/patient/'
        elif user.role == user.Role.DOCTOR:
            return '/dashboard/doctor/'
        elif user.is_superuser:
            return '/dashboard/admin/'
        return '/'


def homepage(request):
    if request.user.is_authenticated:
        if request.user.role == request.user.Role.PATIENT:
            return redirect('patient-dashboard')
        elif request.user.role == request.user.Role.DOCTOR:
            return redirect('doctor-dashboard')
        elif request.user.is_superuser:
            return redirect('admin-dashboard')
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email', '')
            role = request.POST.get('role', 'PATIENT')
            if not username or not password:
                msg = 'Username and password are required.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': msg}, status=400)
                messages.error(request, msg)
                return render(request, 'registration/register.html', status=400)
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                msg = 'Username already exists.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': msg}, status=400)
                messages.error(request, msg)
                return render(request, 'registration/register.html', status=400)
            user = User.objects.create_user(username=username, email=email, password=password)
            if role in dict(User.Role.choices):
                user.role = role
                user.save()
            if user.role == User.Role.PATIENT:
                Patient.objects.create(user=user, age=0, gender='O', contact='')
            elif user.role == User.Role.DOCTOR:
                Doctor.objects.create(user=user, specialization='General', available_days=[], time_slots=[])
            redirect_url = '/login/'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'redirect': redirect_url})
            messages.success(request, "Account created. Please log in.")
            return redirect(redirect_url)
        except IntegrityError as e:
            msg = 'Could not create account: slot / DB constraint error.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, msg)
            return render(request, 'registration/register.html', status=400)
        except Exception as ex:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(ex)}, status=500)
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return render(request, 'registration/register.html', status=500)
    return render(request, 'registration/register.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    def get_success_url(self):
        user = self.request.user
        if user.role == user.Role.PATIENT:
            return '/dashboard/patient/'
        elif user.role == user.Role.DOCTOR:
            return '/dashboard/doctor/'
        elif user.is_superuser:
            return '/dashboard/admin/'
        return '/'

@login_required
def patient_dashboard(request):
    if request.user.role != request.user.Role.PATIENT:
        return HttpResponseForbidden("Forbidden: not a patient")
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user, age=0, gender='O', contact='')
    message = None
    error = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel':
            appt_id = request.POST.get('appointment_id')
            try:
                appt = Appointment.objects.get(pk=appt_id, patient=patient)
            except (Appointment.DoesNotExist, ValueError, TypeError):
                error = "Appointment not found."
            else:
                appt.status = Appointment.Status.CANCELLED
                appt.save()
                message = "Appointment cancelled."
                messages.success(request, message)
        elif action == 'reschedule':
            appt_id = request.POST.get('appointment_id')
            new_date_str = request.POST.get('new_date')
            new_time_slot = request.POST.get('new_time_slot')
            if not (appt_id and new_date_str and new_time_slot):
                error = "All reschedule fields are required."
            else:
                try:
                    appt = Appointment.objects.get(pk=appt_id, patient=patient)
                except (Appointment.DoesNotExist, ValueError, TypeError):
                    error = "Appointment not found."
                else:
                    try:
                        new_date = datetime.datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        error = "Invalid date format. Use YYYY-MM-DD."
                    else:
                        WEEKDAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
                        day_code = WEEKDAY_MAP[new_date.weekday()]
                        doctor = appt.doctor
                        if day_code not in doctor.available_days:
                            error = f"Doctor not available on {new_date.strftime('%A')}."
                        elif new_time_slot not in dict(Doctor.TIME_SLOTS):
                            error = "Invalid time slot."
                        else:
                            try:
                                appt.appointment_date = new_date
                                appt.time_slot = new_time_slot
                                appt.status = Appointment.Status.BOOKED
                                appt.save()
                                message = "Appointment rescheduled successfully."
                                messages.success(request, message)
                            except IntegrityError:
                                error = "Selected slot is already booked for this doctor."
                                messages.error(request, error)
                            except Exception as ex:
                                error = f"Could not reschedule appointment: {ex}"
                                messages.error(request, error)
        else:
            doctor_id = request.POST.get('doctor_id')
            appointment_date_str = request.POST.get('appointment_date')
            time_slot = request.POST.get('time_slot')
            if not (doctor_id and appointment_date_str and time_slot):
                error = "All booking fields are required."
            else:
                try:
                    doctor = Doctor.objects.get(pk=doctor_id)
                except Doctor.DoesNotExist:
                    error = "Selected doctor does not exist."
                else:
                    try:
                        appointment_date = datetime.datetime.strptime(appointment_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        error = "Invalid date format. Use YYYY-MM-DD."
                    else:
                        WEEKDAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
                        day_code = WEEKDAY_MAP[appointment_date.weekday()]
                        if day_code not in doctor.available_days:
                            error = f"Doctor not available on {appointment_date.strftime('%A')}."
                        elif time_slot not in dict(Doctor.TIME_SLOTS):
                            error = "Invalid time slot."
                        else:
                            try:
                                Appointment.objects.create(
                                    doctor=doctor,
                                    patient=patient,
                                    appointment_date=appointment_date,
                                    time_slot=time_slot,
                                )
                                message = "Appointment booked successfully."
                                messages.success(request, message)
                            except IntegrityError:
                                error = "This time slot is already booked for the selected doctor."
                                messages.error(request, error)
                            except Exception as ex:
                                error = f"Could not create appointment: {ex}"
                                messages.error(request, error)
    doctors = Doctor.objects.select_related('user').all()
    appointments = Appointment.objects.filter(patient=patient).order_by('appointment_date', 'time_slot')
    context = {
        'user': request.user,
        'patient': patient,
        'doctors': doctors,
        'appointments': appointments,
        'time_slots': Doctor.TIME_SLOTS,
        'message': message,
        'error': error,
    }
    return render(request, 'appointments/patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if request.user.role != request.user.Role.DOCTOR:
        return HttpResponseForbidden("Forbidden: not a doctor")
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        doctor = Doctor.objects.create(user=request.user, specialization='General', available_days=[], time_slots=[])
    message = None
    error = None
    if request.method == 'POST':
        if request.POST.get('action') == 'update_slots':
            selected_days = request.POST.getlist('available_days')
            selected_slots = request.POST.getlist('time_slots')
            valid_days = {code for code, _ in Doctor.DAYS_OF_WEEK}
            valid_slots = {code for code, _ in Doctor.TIME_SLOTS}
            if not set(selected_days).issubset(valid_days) or not set(selected_slots).issubset(valid_slots):
                error = "Invalid day or time slot selected."
            else:
                doctor.available_days = selected_days
                doctor.time_slots = selected_slots
                doctor.save()
                message = "Availability updated."
                messages.success(request, message)
        elif request.POST.get('action') == 'change_status':
            appt_id = request.POST.get('appointment_id')
            new_action = request.POST.get('status')
            try:
                appt = Appointment.objects.get(pk=appt_id, doctor=doctor)
            except (Appointment.DoesNotExist, ValueError, TypeError):
                error = "Appointment not found."
            else:
                mapping = {
                    'confirm': Appointment.Status.CONFIRMED,
                    'complete': Appointment.Status.COMPLETED,
                    'cancel': Appointment.Status.CANCELLED,
                }
                new_status = mapping.get(new_action)
                if not new_status:
                    error = "Invalid action."
                else:
                    appt.status = new_status
                    appt.save()
                    message = f"Appointment {new_action}ed."
                    messages.success(request, message)
        elif request.POST.get('action') == 'reschedule':
            appt_id = request.POST.get('appointment_id')
            new_date_str = request.POST.get('new_date')
            new_time_slot = request.POST.get('new_time_slot')
            if not (appt_id and new_date_str and new_time_slot):
                error = "All reschedule fields are required."
            else:
                try:
                    appt = Appointment.objects.get(pk=appt_id, doctor=doctor)
                except (Appointment.DoesNotExist, ValueError, TypeError):
                    error = "Appointment not found."
                else:
                    try:
                        new_date = datetime.datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        error = "Invalid date format. Use YYYY-MM-DD."
                    else:
                        WEEKDAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
                        day_code = WEEKDAY_MAP[new_date.weekday()]
                        if day_code not in doctor.available_days:
                            error = f"You are not available on {new_date.strftime('%A')}."
                        elif new_time_slot not in dict(Doctor.TIME_SLOTS):
                            error = "Invalid time slot."
                        else:
                            try:
                                appt.appointment_date = new_date
                                appt.time_slot = new_time_slot
                                appt.save()
                                message = "Appointment rescheduled."
                                messages.success(request, message)
                            except IntegrityError:
                                error = "Selected slot is already booked."
                                messages.error(request, error)
                            except Exception as ex:
                                error = f"Could not reschedule: {ex}"
                                messages.error(request, error)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('appointment_date', 'time_slot')
    context = {
        'user': request.user,
        'doctor': doctor,
        'appointments': appointments,
        'days_choices': Doctor.DAYS_OF_WEEK,
        'time_slots_choices': Doctor.TIME_SLOTS,
        'message': message,
        'error': error,
    }
    return render(request, 'appointments/doctor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden: admin access only")
    return redirect('/admin/')

@login_required
def admin_reports(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden: admin access only")
    return redirect('/admin/')
