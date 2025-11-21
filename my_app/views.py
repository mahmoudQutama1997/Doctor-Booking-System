from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from .models import PatientProfile,DoctorProfile,Speciality,Appointment,Availability,Likes
from django.contrib import messages
import bcrypt
from django.contrib.auth import get_user_model
from datetime import date
from django.contrib.auth import logout
from datetime import datetime
from django.db.models import Prefetch

# Create your views here.
def index(request):
    specialities = Speciality.objects.all()
    doctors=DoctorProfile.objects.all()
    return render(request, "index.html", {"specialities": specialities,"doctors":doctors})

# def register_view(request):
    
   
#     if request.method=='POST':
#         name=request.POST.get('name')
        
#         email=request.POST.get('email')
#         password=request.POST.get('password')
#         hashed_pw=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
#         confirm_password=request.POST.get('cfm_password')
#         has_error=False
       
#         if not name or len(name)<2:
#            messages.error(request,"name is required and must be at least 2 characters")
#            has_error=True
#         if User.objects.filter(email=email).exists():
#            messages.error(request,"email  must be unique")
#            has_error=True
#         if not email or len(email)<8:
#            messages.error(request,"email is required and must be at least 8 characters")
#            has_error=True
#         if password !=confirm_password:
#             messages.error(request,"password not the same")
#             has_error=True
#         if has_error:
        
#             return redirect('main_view')
#         user=User.objects.create(name=name,email=email,password=hashed_pw)
#         request.session['user_id']=user.id
        

#         return redirect('main_view')
#     return render(request,'login.html')


def registration_patient(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        identity = request.FILES.get('identity')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('cfm_password')

        # تحقق من تطابق كلمة المرور
        

        # تشفير كلمة المرور باستخدام bcrypt
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # إنشاء المريض
        user = PatientProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            gender=gender,
            identity=identity,
            email=email,
            password=hashed_pw  # خزن البايتس مباشرة
        )

        # حفظ session للمستخدم
        request.session['user_id'] = user.id
        messages.success(request, f"✅ Account created successfully! Welcome {first_name}!")
        return redirect('index')  # صفحة لوحة المريض

    return render(request, 'registrationpatient.html')
def registration_doctor(request):
    specialities=Speciality.objects.all()
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        password = request.POST.get('password')
        speciality_id = request.POST.get('speciality')
       
        photo = request.FILES.get('photo')
        speciality = Speciality.objects.get(id=speciality_id)

        # التحقق من أن البريد غير مستخدم
        if DoctorProfile.objects.filter(email=email).exists():
            messages.error(request, "❌ هذا البريد مسجل مسبقًا.")
            return redirect('registration_doctor')

        # تشفير كلمة المرور
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
       
        # إنشاء الحساب
        DoctorProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            bio=bio,
            speciality=speciality,
            
            password=hashed_pw,   # نخزنها مشفرة
            photo=photo
        )

        messages.success(request, "✅ تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
        return redirect('doctor_login')

    return render(request, "registrationdoctor.html",{"specialities":specialities})
def login_doctor(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        doctor = DoctorProfile.objects.filter(email=email).first()

        if doctor and doctor.password:
            stored_pw = doctor.password
            if isinstance(stored_pw, str):  # تأكد أن القيمة bytes
                stored_pw = stored_pw.encode()

            if bcrypt.checkpw(password.encode(), stored_pw):
                request.session['doctor_id'] = doctor.id
                messages.success(request, f"👋 مرحبًا {doctor.first_name}!")
                return redirect('doctor_dash')
            else:
                messages.error(request, "❌ كلمة المرور غير صحيحة.")
        else:
            messages.error(request, "❌ البريد الإلكتروني غير موجود.")

    return render(request, "logindoctor.html")
# def submit_login_doctor(request):  
#      specialities = Speciality.objects.all()

#      if request.method=="POST":
#         phone=request.POST.get('phone')  
#         doctor=DoctorProfile.objects.filter(phone=phone).first()
#         if doctor:
#           request.session['doctor_id']=doctor.id
#           return render(request,'doctorpage.html')
#         else:
#           return render(request, 'logindoctor.html', {'specialities': specialities})

#      return render(request, 'logindoctor.html', {'specialities': specialities})

def doctors_by_speciality(request,speciality_id):
     speciality=get_object_or_404(Speciality,id=speciality_id)
     doctors = DoctorProfile.objects.filter(speciality_id=speciality.id)
    
     return render(request, 'doctors_by_speciality.html', {
        'speciality': speciality,
        'doctors': doctors
    })

def appointment_patinet(request):
    doctors = DoctorProfile.objects.all()
    patients = PatientProfile.objects.all()  # ✅ لإرسالهم للـtemplate

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        date = request.POST.get("date")
        time = request.POST.get("time")
        duration_min = request.POST.get("duration_min")
        reason = request.POST.get("reason")

        doctor = DoctorProfile.objects.get(id=doctor_id)
        patient = PatientProfile.objects.get(id=1)

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=date,
            time=time,
            duration_min=duration_min,
            reason=reason
        )

        return redirect('index')

    return render(request, 'appointment.html', {'doctors': doctors, 'patients': patients})
def patient_dash(request):
    # التحقق من أن المريض مسجّل الدخول
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    # جلب المريض أو إعادة التوجيه لو لم يوجد
    try:
        patient = PatientProfile.objects.get(id=user_id)
    except PatientProfile.DoesNotExist:
        return redirect('user_login')
    appointments_prefetch = Prefetch(
      'availability__appointments',
       queryset=Appointment.objects.select_related('patient'),
       to_attr='bookings'
)
    # ✅ جلب الأطباء مع كل availabilities والـ appointments الخاصة بهم
    # ✅ وتصفية المواعيد بحيث تظهر فقط القادمة (date >= اليوم)
    doctors = DoctorProfile.objects.prefetch_related(appointments_prefetch).all()
    liked_doctors=Likes.objects.filter(patient=patient).values_list("doctor_id",flat=True)
    # يمكنك أيضًا تصفية availabilities مباشرة داخل القالب
    # باستخدام شرط {% if slot.date >= today %}

    # تمرير التاريخ الحالي للـ template للمقارنة
    context = {
        'patient': patient,
        'doctors': doctors,
        'today': date.today(),
        'liked_doctors':liked_doctors
    }

    return render(request, "patientdash.html", context)


def doctor_dash(request):
    doctor_id=request.session.get('doctor_id')
    doctor=get_object_or_404(DoctorProfile,id=doctor_id)
    today = date.today()
    availabilities= Availability.objects.filter(doctor=doctor).order_by("-date")
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        messages.error(request, "يرجى تسجيل الدخول أولًا.")
        return redirect('doctor_login')

    doctor = DoctorProfile.objects.get(id=doctor_id)
    likes=Likes.objects.filter(doctor=doctor).select_related("patient")
    return render(request, "doctordash.html", {"doctor": doctor,"availabilities":availabilities,'today': today,"likes":likes})

def user_login(request):
    if request.method=='POST':
        
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=PatientProfile.objects.filter(email=email).first()
        if user:
            if bcrypt.checkpw(password.encode(), user.password):

                request.session['user_id']=user.id
                return redirect('patient_dash')
            else:
                messages.error(request,"invalid credentials")
        else:
            messages.error(request,"user doesnt exist")
            
    return render(request,"patientlogin.html")




def doctor_login(request):
    if request.method=='POST':
        
        email=request.POST.get('email')
        password=request.POST.get('password')
        doctor=DoctorProfile.objects.filter(email=email).first()
        if doctor:
            if bcrypt.checkpw(password.encode(), doctor.password):

                request.session['doctor_id']=doctor.id
                return redirect('doctor_dash')
            else:
                messages.error(request,"invalid credentials")
        else:
            messages.error(request,"user doesnt exist")
            
    return render(request,"logindoctor.html")



def registration_page(request):
    specialities=Speciality.objects.all
    return render(request,"registrationdoctor.html",{"specialities":specialities})


def available_doctor(request):
    doctor_id=request.session.get('doctor_id')
    doctor=get_object_or_404(DoctorProfile,id=doctor_id)
    if request.method=="POST":
        date=request.POST.get('date')
        start_time=request.POST.get('start_time')
        end_time=request.POST.get('end_time')
        slot_duration_min=request.POST.get('slot_duration_min')
        

        Availability.objects.create(
            doctor=doctor,
            date=date,
            start_time=start_time,
            end_time=end_time,
            slot_duration_min=slot_duration_min
            
        )
        return redirect('doctor_dash')
    return render(request,"avaliable.html")

def appointement_patient(request,doctor_id, availability_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    user_id = request.session.get('user_id')
    patient = get_object_or_404(PatientProfile, id=user_id)
    available = get_object_or_404(Availability, id=availability_id, doctor=doctor)

    

    if not doctor_id :
        # ارجع رسالة خطأ أو اعمل redirect
        return render(request, "appointment.html", {"error": "Doctor or patient not selected in session.","patient":patient})

    
    return render(request, "appointment.html", {"error": "Doctor or patient not selected in session.","patient":patient,"doctor":doctor,"available":available})

def cfm_appointment(request, doctor_id,availability_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    available = get_object_or_404(Availability, id=availability_id, doctor=doctor)
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Please log in first.")
            return redirect('login')

        patient = get_object_or_404(PatientProfile, id=user_id)
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        reason = request.POST.get('reason', '').strip()
        date_obj = datetime.strptime(date_str, "%b. %d, %Y").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        existing_appointment = Appointment.objects.filter(
            available=available,
            status="booked"
        ).exists()

        if existing_appointment:
            messages.error(request, "⚠️ This slot is already booked. Please choose another time.")
            return redirect("appointement_patient")  # أو إلى صفحة أخرى مثل قائمة الأطباء

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            available=available,
            date=date_obj,
            time=time_obj,
            reason=reason
        )

        messages.success(request, "Your appointment has been successfully booked!")
        return render(request,"available.html")
    # لو GET request، نرجع المستخدم لصفحة الحجز
    return render(request,"available.html")

def logout_view(request):
    logout(request)
    return redirect('index') 


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import DoctorProfile, PatientProfile, Appointment
from django.urls import reverse
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import DoctorProfile, PatientProfile, Appointment
from django.utils import timezone

def reserve_patient(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    message = ""
    today = timezone.localdate()  # لتصفية الـ slots حسب اليوم

    # ===== POST: محاولة الحجز =====
    if request.method == "POST":
        patient_id = request.session.get("user_id")
        if not patient_id:
            # إذا الطلب Ajax
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "الرجاء تسجيل الدخول"}, status=403)
            return redirect("user_login")

        patient = get_object_or_404(PatientProfile, id=patient_id)
        slot_date = request.POST.get("date")
        slot_time = request.POST.get("time")

        # تحقق إذا Slot محجوز مسبقًا
        existing = Appointment.objects.filter(
            doctor=doctor,
            date=slot_date,
            time=slot_time
        ).exists()

        if existing:
            # Ajax
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "هذا الموعد محجوز بالفعل ❌"}, status=400)
            message = "هذا الموعد محجوز بالفعل ❌"
        else:
            # إنشاء الموعد
            Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date=slot_date,
                time=slot_time,
                status="booked"
            )
            message = "تم حجز الموعد بنجاح ✅"

            # Ajax
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                # ترجع JSON مع رسالة و link لصفحة الحجز
                return JsonResponse({
                    "status": "success",
                    "message": message,
                    "redirect_url": f"/reserve_patient_page/{doctor.id}/"  # عدل الرابط حسب صفحة الحجز عندك
                })

    # ===== GET: عرض صفحة الحجز =====
    patients = PatientProfile.objects.filter(appointments__doctor=doctor).distinct()
    context = {
        "doctor": doctor,
        "patients": patients,
        "message": message,
        "today": today
    }
    return render(request, "reserve_patient.html", context)

def doctor_appointments(request):
    doctor_id = request.session.get("doctor_id")
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    # كل المواعيد لهذا الطبيب
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient')

    return render(request, "appointements.html", {"doctor": doctor, "appointments": appointments})



def like_toggle(request, doctor_id):
    patient_id = request.session.get("user_id")
    if not patient_id:
        return redirect("user_login")

    patient = get_object_or_404(PatientProfile, id=patient_id)
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    like, created = Likes.objects.get_or_create(doctor=doctor, patient=patient)

    if not created:
        # already liked → remove like
        like.delete()
        messages.info(request, "تم إزالة الإعجاب")
    else:
        messages.success(request, "تم تسجيل الإعجاب ❤️")

    return redirect("patient_dash")