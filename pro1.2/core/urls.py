from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Public Pages
    # -----------------------------
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('jobs/', views.jobs_list, name='jobs_list'),

    # -----------------------------
    # Authentication
    # -----------------------------
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # -----------------------------
    # Registration
    # -----------------------------
    path('register/student/', views.student_register, name='student_register'),
    path('register/company/', views.company_registration, name='company_registration'),

    # -----------------------------
    # Job Details & Actions
    # -----------------------------
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/save/', views.save_job, name='save_job'),

    # -----------------------------
    # Student Dashboard
    # -----------------------------
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/edit/', views.edit_student_profile, name='edit_student_profile'),

    # -----------------------------
    # Employer Dashboard
    # -----------------------------
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/profile/edit/', views.edit_employer_profile, name='edit_employer_profile'),
    path('employer/post-job/', views.post_job, name='post_job'),
    path('employer/dashboard/post_job', views.post_job, name='post_job'),

    # -----------------------------
    # Employer Job Applicants
    # -----------------------------
    path('employer/job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('employer/job/<int:job_id>/applicant/<int:applicant_id>/update/', views.update_applicant_status, name='update_applicant_status'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),

]
