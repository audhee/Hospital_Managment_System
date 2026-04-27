import speech_recognition as sr
import pyttsx3
import datetime
import time
from django.core.management.base import BaseCommand
from clinic.models import User, Doctor, Appointment
from django.db.models import Q

class Command(BaseCommand):
    help = 'Starts the AI Voice Agent for Namma Hospital'

    def __init__(self):
        super().__init__()
        # Initialize TTS Engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id) 
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Could not initialize TTS: {e}"))
            self.engine = None

        self.recognizer = sr.Recognizer()

    def speak(self, text):
        # Wait 3 seconds before replying
        time.sleep(3)
        self.stdout.write(f"AI: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.stdout.write(self.style.WARNING("Listening..."))
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                self.stdout.write(f"You said: {text}")
                return text.lower()
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that. Could you repeat?")
                return None
            except Exception as e:
                return None

    def handle(self, *args, **options):
        self.speak("Welcome to Namma Hospital AI Voice Assistant.")
        
        while True:
            self.speak("How can I help? Say: One to Book, Two to Cancel, Three to Reschedule, or Exit.")
            choice = self.listen()

            if not choice: continue

            if 'one' in choice or 'book' in choice:
                self.handle_booking()
            elif 'two' in choice or 'cancel' in choice:
                self.handle_cancel()
            elif 'three' in choice or 'reschedule' in choice:
                self.handle_reschedule()
            elif 'exit' in choice or 'quit' in choice:
                self.speak("Goodbye!")
                break

    def handle_booking(self):
        depts = list(Doctor.objects.values_list('specialization', flat=True).distinct())
        if not depts:
            self.speak("No doctors available.")
            return

        dept_str = ", ".join([f"{i+1} for {d}" for i, d in enumerate(depts)])
        self.speak(f"Which department? Say {dept_str}")
        dept_choice = self.listen()
        
        selected_dept = next((d for i, d in enumerate(depts) if str(i+1) in str(dept_choice) or d.lower() in str(dept_choice)), None)
        if not selected_dept:
            self.speak("Department not found.")
            return

        doctors = Doctor.objects.filter(specialization=selected_dept)
        doc_list = [f"Dr. {d.user.username}" for d in doctors]
        self.speak(f"In {selected_dept}, we have {', '.join(doc_list)}. Say the doctor's name.")
        doc_choice = self.listen()
        
        selected_doc = next((d for d in doctors if d.user.username.lower() in str(doc_choice)), None)
        if not selected_doc:
            self.speak("Doctor not found.")
            return

        # Typed Inputs
        self.speak("Please TYPE the date (YYYY-MM-DD):")
        date_str = input("Enter Date: ").strip()

        self.speak("Please TYPE the time (HH:MM):")
        time_str = input("Enter Time: ").strip()

        self.speak("What is the reason? (Please speak now)")
        desc = self.listen() or "No description"

        self.speak(f"Confirming Dr. {selected_doc.user.username} on {date_str} at {time_str}. Say Yes to confirm.")
        confirm = self.listen()
        
        if 'yes' in str(confirm):
            self.speak("Please TYPE your username:")
            patient_name = input("Enter Username: ").strip()
            try:
                patient = User.objects.get(username__icontains=patient_name)
                Appointment.objects.create(
                    patient=patient,
                    doctor=selected_doc.user,
                    date=date_str,
                    time=time_str,
                    description=desc
                )
                self.speak("Appointment Booked Successfully!")
            except Exception as e:
                self.speak(f"Error: {e}")
        else:
            self.speak("Booking Cancelled.")

    def handle_cancel(self):
        self.speak("Please TYPE your username:")
        patient_name = input("Enter Username: ").strip()
        if not patient_name: return

        try:
            patient = User.objects.get(username__icontains=patient_name)
            appts = Appointment.objects.filter(patient=patient, status='Pending')
            
            if not appts.exists():
                self.speak(f"No pending appointments found for {patient_name}.")
                return

            appt_list = list(appts)
            for i, appt in enumerate(appt_list):
                self.speak(f"Option {i+1}: with Dr. {appt.doctor.username} on {appt.date}.")
            
            self.speak("Please TYPE the option number you want to cancel.")
            cancel_choice = input("Enter Option Number: ").strip()
            
            try:
                selected_index = int(cancel_choice) - 1
                if 0 <= selected_index < len(appt_list):
                    appt_to_cancel = appt_list[selected_index]
                    # We use delete() to remove it entirely
                    appt_to_cancel.delete()
                    self.speak("Appointment Cancelled successfully!")
                else:
                    self.speak("Invalid option number.")
            except ValueError:
                self.speak("Please enter a valid number.")
        except Exception as e:
            self.speak(f"Error: {e}")

    def handle_reschedule(self):
        self.speak("Please TYPE your username:")
        patient_name = input("Enter Username: ").strip()
        if not patient_name: return

        try:
            patient = User.objects.get(username__icontains=patient_name)
            appts = Appointment.objects.filter(patient=patient, status='Pending')
            
            if not appts.exists():
                self.speak("No appointments found.")
                return

            appt_list = list(appts)
            for i, appt in enumerate(appt_list):
                self.speak(f"Option {i+1}: with Dr. {appt.doctor.username} on {appt.date}.")
            
            self.speak("Please TYPE the option number to reschedule.")
            choice = input("Enter Option Number: ").strip()
            
            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(appt_list):
                    appt = appt_list[selected_index]
                    self.speak("TYPE the new date (YYYY-MM-DD):")
                    appt.date = input("New Date: ").strip()
                    self.speak("TYPE the new time (HH:MM):")
                    appt.time = input("New Time: ").strip()
                    appt.save()
                    self.speak("Rescheduled successfully!")
                else:
                    self.speak("Invalid option.")
            except ValueError:
                self.speak("Please enter a valid number.")
        except Exception as e:
            self.speak("Error during reschedule.")
