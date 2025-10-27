from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/patient/', views.patient_dashboard, name='patient-dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor-dashboard'),
    # removed admin-dashboard and reports routes so only /admin/ (project urls) exposes admin
]
