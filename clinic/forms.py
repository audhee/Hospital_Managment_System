from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Appointment, DoctorSchedule, DoctorDayConfig, Doctor

# 1. Patient Signup Form
class PatientSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# 2. Doctor Signup Form
class DoctorSignupForm(UserCreationForm):
    specialization = forms.CharField(max_length=100)
    dept = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                dept=self.cleaned_data.get('dept')
            )
        return user

# 3. Appointment Booking Form
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'placeholder': 'Optional: Reason for visit', 'rows': 3}),
        }


