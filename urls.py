from django.contrib import admin
from django.urls import path
from appointments import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),

    # Dashboards
    path('dashboard/patient/', views.patient_dashboard, name='patient-dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor-dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/admin/reports/', views.admin_reports, name='admin-reports'),

    # Homepage
    path('', views.homepage, name='index'),
]
