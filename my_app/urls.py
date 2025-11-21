from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index ,name='index'),
     path('registration/patient/', views.registration_patient ,name='registration_patient'),
     path('registration/page/', views.registration_page ,name='registration_page'),
     path('registration/doctor/', views.registration_doctor ,name='registration_doctor'),
      path('login/doctor/', views.login_doctor ,name='login_doctor'),
      path('doctors_by_speciality/<int:speciality_id>/', views.doctors_by_speciality ,name='doctors_by_speciality'),
       path('appointement/', views.appointment_patinet ,name='appointment_patinet'),
        path('user_login/', views.user_login ,name='user_login'),
         path('patientDashboard/', views.patient_dash ,name='patient_dash'),
          path('doctor_login/', views.doctor_login ,name='doctor_login'),
         path('doctorDashboard/', views.doctor_dash ,name='doctor_dash'),
         path('availableDoctor/', views.available_doctor ,name='available_doctor'),
         path('AppointmentDoctor/<int:doctor_id>/<int:availability_id>/', views.appointement_patient, name='appointement_patient'),
         
          path('logout/', views.logout_view, name='logout'),
        path("cfm_appointment/<int:doctor_id>/", views.cfm_appointment, name="cfm_appointment"),
        path("cfm_reservation/<int:doctor_id>/", views.reserve_patient, name="reserve_patient"),
        path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
        path("doctor/<int:doctor_id>/like/", views.like_toggle, name="like_toggle"),



]