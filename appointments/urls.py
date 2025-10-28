# clinic_system/urls.py (or your main project urls.py)

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from appointments import views  # assuming your app is named 'appointments'

urlpatterns = [
    
    # Admin
    path('admin/', admin.site.urls),

    # Homepage
    path('', views.homepage, name='homepage'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='homepage'), name='logout'),
    path('register/', views.register, name='register'),

    # Dashboards
    path('dashboard/patient/', views.patient_dashboard, name='patient-dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor-dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),

    # Admin reports (optional)
    path('dashboard/admin/reports/', views.admin_reports, name='admin-reports'),
]

