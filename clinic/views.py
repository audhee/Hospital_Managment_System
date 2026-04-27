from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from .forms import PatientSignupForm, AppointmentForm
from .models import User, Doctor, Appointment
from django.contrib.auth.decorators import login_required
from django import forms

# 1. The Home View (The one Django is complaining about)
def home(request):
    return render(request, 'clinic/home.html')

# 2. The Signup View
def signup_view(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_patient = True  
            user.save()
            login(request, user)  
            return redirect('home')
    else:
        form = PatientSignupForm()
    return render(request, 'clinic/signup.html', {'form': form})

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'clinic/doctor_list.html',{'doctors':doctors})


@login_required
def book_appointment(request):
    doctor_id = request.GET.get('doctor')
    
    if not doctor_id:
        # If no doctor is specified in URL, force them to select one
        messages.info(request, "Please select a doctor first to book an appointment.")
        return redirect('doctor_list')
        
    try:
        selected_doctor = User.objects.get(pk=doctor_id, is_doctor=True)
    except (User.DoesNotExist, ValueError):
        messages.error(request, "Invalid doctor selected.")
        return redirect('doctor_list')
            
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = selected_doctor
            appointment.save()
            messages.success(request, f"Appointment successfully booked with Dr. {selected_doctor.get_full_name() or selected_doctor.username}.")
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
            
    return render(request, 'clinic/book_appointment.html', {'form': form, 'doctor': selected_doctor})

@login_required
def patient_dashboard(request):
    if request.user.is_doctor:
        return redirect('doctor_dashboard')
    
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'clinic/patient_dashboard.html', {'appointments': appointments})

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('patient_dashboard')
    appointments = Appointment.objects.filter(doctor=request.user)

    return render(request, 'clinic/doctor_dashboard.html', {'appointments': appointments})