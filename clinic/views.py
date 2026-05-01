from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from .forms import PatientSignupForm, AppointmentForm, DoctorSignupForm
from .models import User, Doctor, Appointment, DoctorSchedule, DoctorLeave, DoctorDayConfig
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from django.http import JsonResponse

# 1. The Home View (The one Django is complaining about)
def home(request):
    return render(request, 'clinic/home.html')

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

def doctor_signup_view(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('doctor_dashboard')
    else:
        form = DoctorSignupForm()
    return render(request, 'clinic/signup.html', {'form': form, 'title': 'Doctor Registration'})

def doctor_list(request):
    doctors = Doctor.objects.all()
    selected_date = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    
    from .utils import get_doctor_working_hours
    
    doctor_data = []
    for doctor in doctors:
        status_info = get_doctor_working_hours(doctor.user.id, selected_date)
        
        doctor_data.append({
            'doctor': doctor,
            'status_info': status_info
        })
        
    return render(request, 'clinic/doctor_list.html', {
        'doctor_data': doctor_data,
        'selected_date': selected_date
    })


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
            appt_date = form.cleaned_data['date']
            appt_time = form.cleaned_data['time']
            
            # Convert to strings for the utility function
            date_str = appt_date.strftime('%Y-%m-%d')
            time_str = appt_time.strftime('%H:%M')
            
            from .utils import validate_appointment_time, find_next_available_slot
            
            validation = validate_appointment_time(selected_doctor.id, date_str, time_str)
            
            if not validation['is_valid']:
                next_slot = find_next_available_slot(selected_doctor.id, date_str)
                messages.error(request, f"Sorry, this time is taken or invalid: {validation['error']} The next available time is {next_slot}.")
            else:
                appointment = form.save(commit=False)
                appointment.patient = request.user
                appointment.doctor = selected_doctor
                appointment.status = 'Confirmed'
                appointment.save()
                
                messages.success(request, f"Appointment CONFIRMED with Dr. {selected_doctor.get_full_name() or selected_doctor.username} at {time_str} on {date_str}!")
                return redirect('patient_dashboard')
    else:
        # Pre-fill date if passed in URL
        initial_data = {}
        date_param = request.GET.get('date')
        if date_param:
            initial_data['date'] = date_param
        form = AppointmentForm(initial=initial_data)
            
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
    
    doctor = request.user.doctor
    
    # Check if doctor has set up their schedule
    if not DoctorSchedule.objects.filter(doctor=doctor).exists():
        messages.info(request, "Welcome! Please set up your working hours and capacity before you start.")
        return redirect('manage_schedule')

    appointments = Appointment.objects.filter(doctor=request.user)
    doctor_schedules = DoctorSchedule.objects.filter(doctor=doctor).order_by('day_of_week')

    return render(request, 'clinic/doctor_dashboard.html', {
        'appointments': appointments,
        'doctor_schedules': doctor_schedules
    })

@login_required
def download_appointment_pdf(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user is either the patient or the doctor
    if request.user != appointment.patient and request.user != appointment.doctor:
        messages.error(request, "You are not authorized to download this PDF.")
        return redirect('home')

    template_path = 'clinic/appointment_pdf.html'
    context = {
        'appointment': appointment,
        'now': timezone.now(),
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="appointment_{appointment_id}.pdf"'
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def manage_schedule(request):
    if not request.user.is_doctor:
        return redirect('patient_dashboard')
    
    doctor = request.user.doctor
    
    days_of_week = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    
    if request.method == 'POST':
        # Clear existing schedules for this doctor
        DoctorSchedule.objects.filter(doctor=doctor).delete()
        DoctorDayConfig.objects.filter(doctor=doctor).delete()
        
        for day_int, day_name in days_of_week:
            is_active = request.POST.get(f'day_{day_int}_active') == 'on'
            if is_active:
                start_time = request.POST.get(f'day_{day_int}_start')
                end_time = request.POST.get(f'day_{day_int}_end')
                slot_duration = request.POST.get(f'day_{day_int}_duration')
                max_appointments = request.POST.get(f'day_{day_int}_capacity')
                
                if start_time and end_time and slot_duration and max_appointments:
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        day_of_week=day_int,
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration_minutes=int(slot_duration)
                    )
                    DoctorDayConfig.objects.create(
                        doctor=doctor,
                        day_of_week=day_int,
                        max_appointments=int(max_appointments)
                    )
        
        messages.success(request, "Schedule updated successfully!")
        return redirect('doctor_dashboard')
        
    else:
        schedule_data = []
        for day_int, day_name in days_of_week:
            sched = DoctorSchedule.objects.filter(doctor=doctor, day_of_week=day_int).first()
            config = DoctorDayConfig.objects.filter(doctor=doctor, day_of_week=day_int).first()
            
            schedule_data.append({
                'day_int': day_int,
                'day_name': day_name,
                'is_active': sched is not None,
                'start_time': sched.start_time.strftime('%H:%M') if sched else '09:00',
                'end_time': sched.end_time.strftime('%H:%M') if sched else '17:00',
                'slot_duration': sched.slot_duration_minutes if sched else 30,
                'max_appointments': config.max_appointments if config else 20
            })
            
    return render(request, 'clinic/manage_schedule.html', {'schedule_data': schedule_data})

def available_slots_api(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({"error": "doctor_id and date parameters are required."}, status=400)

    from .utils import get_doctor_working_hours
    status_info = get_doctor_working_hours(doctor_id, date_str)
    
    if "error" in status_info:
        status_code = status_info.get("status", 400)
        return JsonResponse({"error": status_info["error"]}, status=status_code)

    return JsonResponse(status_info)

@login_required
def update_appointment_status(request, appointment_id, new_status):
    if not request.user.is_doctor:
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if new_status in ['Confirmed', 'Cancelled']:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment status updated to {new_status}.")
    
    return redirect('doctor_dashboard')