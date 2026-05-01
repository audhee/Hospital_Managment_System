from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Ensure this name is exactly 'urlpatterns'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/doctor/', views.doctor_signup_view, name='doctor_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='clinic/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors-panel/', views.doctor_dashboard, name='doctor_dashboard'),
    path('manage-schedule/', views.manage_schedule, name='manage_schedule'),
    path('appointment/<int:appointment_id>/pdf/', views.download_appointment_pdf, name='download_appointment_pdf'),
    path('api/slots/available/', views.available_slots_api, name='available_slots_api'),
    path('appointment/<int:appointment_id>/status/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
]