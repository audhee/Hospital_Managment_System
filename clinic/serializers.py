from rest_framework import serializers
from clinic.models import Appointment, User

class AIBookingSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    call_id = serializers.CharField(max_length=100, required=False, allow_null=True)

    def validate_doctor_id(self, value):
        if not User.objects.filter(pk=value, is_doctor=True).exists():
            raise serializers.ValidationError("Valid doctor ID is required.")
        return value

    def validate_patient_id(self, value):
        if not User.objects.filter(pk=value, is_patient=True).exists():
            raise serializers.ValidationError("Valid patient ID is required.")
        return value
