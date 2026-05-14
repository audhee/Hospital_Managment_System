from django.db import transaction
from django.core.exceptions import ValidationError
from clinic.models import Appointment, User
from clinic.utils import validate_appointment_time

class AppointmentService:
    @staticmethod
    def book_appointment_via_ai(doctor_id, patient_id, date_str, time_str, call_id=None):
        """
        Creates an appointment safely using a database transaction.
        Returns the created Appointment object or raises ValidationError.
        """
        with transaction.atomic():
            # Idempotency check: if this call_id already created an appointment, return it
            if call_id:
                existing_appt = Appointment.objects.filter(call_id=call_id).first()
                if existing_appt:
                    return existing_appt

            # Re-validate the appointment time INSIDE the transaction block
            # In a very high concurrency environment, we would also add select_for_update() 
            # on the DoctorDayConfig here to acquire a row-level lock.
            validation = validate_appointment_time(doctor_id, date_str, time_str)
            
            if not validation.get('is_valid'):
                raise ValidationError(validation.get('error', 'Invalid appointment time.'))
            
            try:
                doctor_user = User.objects.get(pk=doctor_id, is_doctor=True)
                patient_user = User.objects.get(pk=patient_id, is_patient=True)
            except User.DoesNotExist:
                raise ValidationError("Invalid doctor or patient ID.")
                
            appointment = Appointment.objects.create(
                doctor=doctor_user,
                patient=patient_user,
                date=date_str,
                time=time_str,
                description="Booked via AI Voice Agent",
                status='Confirmed',
                source='voice_ai',
                call_id=call_id
            )
            
            return appointment
