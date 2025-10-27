from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect

def index(request):
    # If user is authenticated, send them to their dashboard based on role
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if request.user.is_superuser or role == 'ADMIN':
            return redirect('admin-dashboard')
        if role == 'DOCTOR':
            return redirect('doctor-dashboard')
        return redirect('patient-dashboard')
    # Unauthenticated visitors: render the styled index template
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('', include('appointments.urls')),  # app-level routes (login, register, dashboards)
]
