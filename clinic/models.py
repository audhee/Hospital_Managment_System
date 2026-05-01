from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to = 'profile_pics/', null = True, blank = True)
    """
    is_doctor → is this user a doctor?
    is_patient → is this user a patient?
    profile_pic → user's image
    """

class Doctor(models.Model): # A table "Doctor" will be created
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True) # One to one each doctor is linked to one user and each user linked to one doctor
    specialization = models.CharField(max_length=100)
    dept = models.CharField(max_length = 100, default = "General")

    def __str__(self): # __str__ is a special method in Python, It tells Django (and Python) how to display your object as text
        return f"Dr. {self.user.first_name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed','Confirmed'),
        ('Completed','Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.username}"

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[(i, i) for i in range(7)]) # 0-6 (Mon-Sun)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.doctor} - Day {self.day_of_week} ({self.start_time}-{self.end_time})"

    class Meta:
        unique_together = ('doctor', 'day_of_week')

class DoctorLeave(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leaves')
    leave_date = models.DateField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.doctor} on {self.leave_date}"

    class Meta:
        unique_together = ('doctor', 'leave_date')

class DoctorDayConfig(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='day_configs')
    day_of_week = models.IntegerField(choices=[(i, i) for i in range(7)])
    max_appointments = models.IntegerField()

    def __str__(self):
        return f"{self.doctor} Day {self.day_of_week} - Max {self.max_appointments}"

    class Meta:
        unique_together = ('doctor', 'day_of_week')