from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .serializers import AIBookingSerializer
from .services.appointment_service import AppointmentService

class BookAppointmentAPIView(APIView):
    """
    Endpoint for AI Voice Agent to book appointments.
    """
    # Note: In production, we should add AuthenticationClasses (Token/JWT)
    
    def post(self, request, *args, **kwargs):
        serializer = AIBookingSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                # Call the dedicated service layer
                appointment = AppointmentService.book_appointment_via_ai(
                    doctor_id=data['doctor_id'],
                    patient_id=data['patient_id'],
                    date_str=data['date'].strftime('%Y-%m-%d'),
                    time_str=data['time'].strftime('%H:%M'),
                    call_id=data.get('call_id')
                )
                
                return Response({
                    "status": "success",
                    "message": "Appointment booked successfully.",
                    "appointment_id": appointment.id,
                    "doctor": str(appointment.doctor),
                    "patient": str(appointment.patient),
                    "date": appointment.date.strftime('%Y-%m-%d'),
                    "time": appointment.time.strftime('%H:%M'),
                    "call_id": appointment.call_id
                }, status=status.HTTP_201_CREATED)
                
            except ValidationError as e:
                return Response({
                    "status": "error",
                    "message": str(e.message) if hasattr(e, 'message') else str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "An unexpected error occurred during booking."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
