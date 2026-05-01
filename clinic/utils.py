from datetime import datetime, timedelta, date as datetime_date
from django.utils import timezone
from .models import Doctor, DoctorSchedule, DoctorLeave, DoctorDayConfig, Appointment

def validate_appointment_time(doctor_id, date_str, time_str):
    """
    Validates if a specific time is available for booking.
    Returns: {"is_valid": True/False, "error": "Reason"}
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        target_time = datetime.strptime(time_str, '%H:%M').time()
        target_datetime = datetime.combine(target_date, target_time)
    except ValueError:
        return {"is_valid": False, "error": "Invalid date or time format."}

    if target_date < timezone.now().date():
        return {"is_valid": False, "error": "Cannot book appointments in the past."}
    
    if target_date == timezone.now().date() and target_time < timezone.now().time():
        return {"is_valid": False, "error": "Cannot book appointments in the past."}

    if not Doctor.objects.filter(pk=doctor_id).exists():
        return {"is_valid": False, "error": "Doctor not found."}

    # 1. Leave Check
    if DoctorLeave.objects.filter(doctor_id=doctor_id, leave_date=target_date).exists():
        return {"is_valid": False, "error": "Doctor is on leave this day."}

    day_of_week = target_date.weekday()

    # 2. Schedule Check
    schedules = DoctorSchedule.objects.filter(doctor_id=doctor_id, day_of_week=day_of_week)
    if not schedules.exists():
        return {"is_valid": False, "error": "Doctor does not work on this day."}

    schedule = schedules.first()
    slot_duration = timedelta(minutes=schedule.slot_duration_minutes)
    
    start_dt = datetime.combine(target_date, schedule.start_time)
    end_dt = datetime.combine(target_date, schedule.end_time)
    requested_end_dt = target_datetime + slot_duration

    if target_datetime < start_dt or requested_end_dt > end_dt:
        return {"is_valid": False, "error": f"Time is outside working hours ({schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')})."}

    # 3. Capacity Check
    day_config = DoctorDayConfig.objects.filter(doctor_id=doctor_id, day_of_week=day_of_week).first()
    max_appointments = day_config.max_appointments if day_config else None

    booked_appointments = Appointment.objects.filter(
        doctor_id=doctor_id, 
        date=target_date
    ).exclude(status__in=['Cancelled', 'Completed'])

    if max_appointments is not None and booked_appointments.count() >= max_appointments:
        return {"is_valid": False, "error": "Doctor has reached maximum capacity for this day."}

    # 4. Overlap Check
    for app in booked_appointments:
        app_start = datetime.combine(target_date, app.time)
        app_end = app_start + slot_duration
        
        # Overlap condition
        if target_datetime < app_end and requested_end_dt > app_start:
            return {"is_valid": False, "error": "Time overlaps with another booked appointment."}

    return {"is_valid": True}

def find_next_available_slot(doctor_id, start_date_str):
    """
    Scans forward from start_date to find the next available time slot.
    """
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    
    for day_offset in range(30): # Scan up to 30 days ahead
        check_date = start_date + timedelta(days=day_offset)
        
        if check_date < timezone.now().date():
            continue
            
        if DoctorLeave.objects.filter(doctor_id=doctor_id, leave_date=check_date).exists():
            continue
            
        day_of_week = check_date.weekday()
        schedule = DoctorSchedule.objects.filter(doctor_id=doctor_id, day_of_week=day_of_week).first()
        if not schedule:
            continue
            
        day_config = DoctorDayConfig.objects.filter(doctor_id=doctor_id, day_of_week=day_of_week).first()
        max_appointments = day_config.max_appointments if day_config else None
        
        booked_appointments = Appointment.objects.filter(
            doctor_id=doctor_id, 
            date=check_date
        ).exclude(status__in=['Cancelled', 'Completed'])
        
        if max_appointments is not None and booked_appointments.count() >= max_appointments:
            continue
            
        slot_duration = timedelta(minutes=schedule.slot_duration_minutes)
        current_dt = datetime.combine(check_date, schedule.start_time)
        end_dt = datetime.combine(check_date, schedule.end_time)

        while current_dt + slot_duration <= end_dt:
            if check_date == timezone.now().date() and current_dt.time() <= timezone.now().time():
                current_dt += timedelta(minutes=5)
                continue
                
            is_overlapping = False
            requested_end = current_dt + slot_duration
            
            for app in booked_appointments:
                app_start = datetime.combine(check_date, app.time)
                app_end = app_start + slot_duration
                if current_dt < app_end and requested_end > app_start:
                    is_overlapping = True
                    break
                    
            if not is_overlapping:
                return f"{current_dt.strftime('%I:%M %p')} on {check_date.strftime('%Y-%m-%d')}"
                
            current_dt += timedelta(minutes=5)
            
    return "No available slots found in the next 30 days."

def get_doctor_working_hours(doctor_id, date_str):
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Invalid date format.", "status": 400}
        
    day_of_week = target_date.weekday()
    schedule = DoctorSchedule.objects.filter(doctor_id=doctor_id, day_of_week=day_of_week).first()
    
    if DoctorLeave.objects.filter(doctor_id=doctor_id, leave_date=target_date).exists():
        return {"doctor_status": "On Leave"}
        
    if not schedule:
        return {"doctor_status": "Not Working"}
        
    return {
        "doctor_status": "Available",
        "working_hours": f"{schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')}"
    }
