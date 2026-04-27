from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Ensure this name is exactly 'urlpatterns'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='clinic/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors-panel/', views.doctor_dashboard, name='doctor_dashboard'),
]