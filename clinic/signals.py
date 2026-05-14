from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Appointment

@receiver(post_save, sender=Appointment)
def broadcast_appointment_update(sender, instance, created, **kwargs):
    """
    Signal receiver to broadcast real-time updates when an appointment is created or modified.
    """
    channel_layer = get_channel_layer()
    doctor_group = f"doctor_{instance.doctor.id}"
    
    event_type = "created" if created else "updated"
    
    message = {
        "event": event_type,
        "appointment_id": instance.id,
        "patient": str(instance.patient),
        "date": instance.date.strftime('%Y-%m-%d'),
        "time": instance.time.strftime('%H:%M'),
        "status": instance.status,
        "source": instance.source,
    }

    # Send message to the doctor's channel group
    async_to_sync(channel_layer.group_send)(
        doctor_group,
        {
            "type": "appointment_update",
            "message": message
        }
    )
