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
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.username}"