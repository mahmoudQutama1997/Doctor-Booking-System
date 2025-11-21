from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class BaseProfile(models.Model):
    first_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("M", "Male"), ("F", "Female")],
        blank=True
    )
    identity = models.FileField(upload_to='identities/', blank=True, null=True)

    class Meta:
        abstract = True  # ⚠️ هذا يخليه مجرد كلاس أساسي فقط
# Create your models here.
class PatientProfile(BaseProfile):
    
    identity=models.FileField()
    phone=models.CharField(max_length=20)
    email=models.CharField(null=True)
    password=models.BinaryField(max_length=20,null=True)
    birth_date=models.DateField(blank=True,null=True)
    gender=models.CharField(max_length=10,choices=[("M","Male"),("F","Female")],blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Speciality(models.Model):
    name = models.CharField(max_length=100)
    icon = models.URLField(max_length=300, blank=True, null=True)
    def __str__(self):
        return self.name
       
class DoctorProfile(BaseProfile):
    bio=models.TextField(blank=True)
    email=models.CharField(null=True)
    password=models.BinaryField(max_length=20,null=True)
    phone=models.CharField(max_length=20)
    clinic_name=models.CharField(max_length=120,blank=True)
    address=models.CharField(max_length=200,blank=True)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)

    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, related_name='specialities')

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"


class Availability(models.Model):
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="availability")
    date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    slot_duration_min=models.PositiveIntegerField(default=30)
    is_booked = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    STATUS_CHOICES=[
        ("booked","Booked"),
        ("cancelled","Cancelled"),
        ("completed","Completed")
    ]
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="appointments")
    patient=models.ForeignKey(PatientProfile,on_delete=models.CASCADE,related_name="appointments")
    availability = models.ForeignKey(
        Availability,
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,    # ✅ يسمح بأن يكون فارغًا
        blank=True    # ✅ يسمح للنماذج أن تتركه فارغًا
    )
    date=models.DateField()
    time=models.TimeField()
    duration_min=models.PositiveIntegerField(default=30)
    reason=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='booked')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
       unique_together = ("doctor", "date", "time")
    def __str__(self):
        return f"{self.date} {self.time} — {self.doctor} / {self.patient}"


class Likes(models.Model):
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="likes")
    patient=models.ForeignKey(PatientProfile,on_delete=models.CASCADE,related_name="likes_doctor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'patient')  # يمنع تكرار اللايك

    def __str__(self):
        return f"{self.patient.first_name} liked {self.doctor.first_name}"
    