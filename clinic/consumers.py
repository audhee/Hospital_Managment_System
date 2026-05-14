import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DoctorDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated doctors to connect
        if self.scope["user"].is_anonymous or not getattr(self.scope["user"], 'is_doctor', False):
            await self.close()
            return

        self.doctor_id = self.scope["user"].id
        self.group_name = f"doctor_{self.doctor_id}"

        # Join doctor-specific group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave doctor-specific group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def appointment_update(self, event):
        """
        Handle messages sent to the doctor group.
        """
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "appointment_update",
            "data": message
        }))
