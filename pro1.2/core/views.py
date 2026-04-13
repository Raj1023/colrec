from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Job, Notification, Application, SavedJob

User = get_user_model()

# -----------------------------
# Welcome / Home Page
# -----------------------------
def welcome(request):
    latest_jobs = Job.objects.order_by('-created_at')[:6]
    return render(request, 'home/welcome.html', {'jobs': latest_jobs})

# -----------------------------
# Jobs List Page (All Jobs + Search + Filter)
# -----------------------------
def jobs_list(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    experience = request.GET.get('experience', '')
    location = request.GET.get('location', '')

    jobs = Job.objects.all().order_by('-created_at')

    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(skills__icontains=query))
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience:
        jobs = jobs.filter(experience=experience)
    if location:
        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home/jobs_list.html', {
        'jobs': page_obj,
        'query': query,
        'job_type': job_type,
        'experience': experience,
        'location': location
    })

# -----------------------------
# Job Detail Page
# -----------------------------
@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user = request.user
    already_applied = False
    already_saved = False
    if user.role == 'student':
        already_applied = Application.objects.filter(job=job, applicant=user).exists()
        already_saved = SavedJob.objects.filter(job=job, user=user).exists()

    return render(request, 'home/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'already_saved': already_saved
    })

# -----------------------------
# Apply Job
# -----------------------------
@login_required
def apply_job(request, job_id):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Only students can apply for jobs.")
        return redirect('jobs_list')

    job = get_object_or_404(Job, id=job_id)
    if Application.objects.filter(applicant=user, job=job).exists():
        messages.warning(request, "You already applied for this job.")
    else:
        Application.objects.create(applicant=user, job=job)
        messages.success(request, f"Applied for {job.title} at {job.company}.")
    return redirect(request.META.get('HTTP_REFERER', 'jobs_list'))

# -----------------------------
# Save Job
# -----------------------------
@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user = request.user
    if user.role != 'student':
        messages.error(request, "Only students can save jobs.")
        return redirect('jobs_list')

    saved, created = SavedJob.objects.get_or_create(user=user, job=job)
    if created:
        messages.success(request, "Job saved successfully!")
    else:
        messages.info(request, "Job already saved.")
    return redirect(request.META.get('HTTP_REFERER', 'jobs_list'))

# -----------------------------
# Company Registration
# -----------------------------
def company_registration(request):
    if request.method == 'POST':
        company_name = request.POST.get('cname')
        hr_name = request.POST.get('hrname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        website = request.POST.get('website')
        industry = request.POST.get('industry')
        description = request.POST.get('desc')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Company with this email already exists.")
            return redirect('company_registration')

        User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            role='employer',
            company_name=company_name,
            hr_name=hr_name,
            phone_number=phone_number,
            website=website,
            industry=industry,
            description=description
        )
        messages.success(request, "Company registered successfully! Please login.")
        return redirect('login')

    return render(request, 'home/company_registration.html')

# -----------------------------
# Student Registration
# -----------------------------
def student_register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        roll = request.POST.get('roll')
        department = request.POST.get('department')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Student with this email already exists.")
        else:
            User.objects.create(
                username=email,
                first_name=fullname,
                email=email,
                password=make_password(password),
                role='student',
                department=department,
                roll_number=roll
            )
            messages.success(request, "Student registered successfully! Please login.")
            return redirect('login')
    return render(request, 'home/student_registration.html')

# -----------------------------
# Login / Logout
# -----------------------------
def login(request):
    if request.method == 'POST':
        email = request.POST.get('Email') or request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'employer':
                return redirect('employer_dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, 'home/login.html')

def logout(request):
    auth_logout(request)
    return redirect('welcome')

# -----------------------------
# Static Pages
# -----------------------------
def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

# -----------------------------
# Student Dashboard
# -----------------------------
@login_required
def student_dashboard(request):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Unauthorized access.")
        return redirect('welcome')

    jobs = Job.objects.all().order_by('deadline')
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    applied_jobs = Application.objects.filter(applicant=user)
    saved_jobs = SavedJob.objects.filter(user=user)

    return render(request, 'home/dashboard.html', {
        'user': user,
        'jobs': jobs,
        'notifications': notifications,
        'applied_jobs': applied_jobs,
        'saved_jobs': saved_jobs
    })

# -----------------------------
# Employer Dashboard
# -----------------------------
@login_required
def employer_dashboard(request):
    user = request.user
    if user.role != 'employer':
        messages.error(request, "Unauthorized access.")
        return redirect('login')
    jobs = Job.objects.filter(posted_by=user)
    return render(request, 'home/cdashboard.html', {'user': user, 'jobs': jobs})

# -----------------------------
# Post Job
# -----------------------------
@login_required
def post_job(request):
    if request.user.role != 'employer':
        messages.error(request, "Access denied! Only recruiters can post jobs.")
        return redirect('welcome')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        requirements = request.POST.get('requirements')
        deadline = request.POST.get('deadline')
        job_type = request.POST.get('job_type')
        experience = request.POST.get('experience')
        skills = request.POST.get('skills', '')  # optional

        if not title or not description or not location or not job_type or not experience:
            messages.error(request, "Please fill all required fields.")
            return render(request, 'home/post_job.html', {
                'title': title,
                'description': description,
                'location': location,
                'salary': salary,
                'requirements': requirements,
                'deadline': deadline,
                'job_type': job_type,
                'experience': experience,
                'skills': skills
            })

        Job.objects.create(
            posted_by=request.user,
            company=request.user.company_name,
            title=title,
            description=description,
            location=location,
            salary=salary if salary else None,
            requirements=requirements if requirements else "",
            skills=skills,
            deadline=deadline if deadline else None,
            job_type=job_type,
            experience=experience
        )

        messages.success(request, "Job posted successfully!")
        return redirect('employer_dashboard')

    return render(request, 'home/post_job.html')

# -----------------------------
# Job Applicants
# -----------------------------
@login_required
def job_applicants(request, job_id):
    user = request.user
    if user.role != 'employer':
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    job = get_object_or_404(Job, id=job_id, posted_by=user)
    applicants = Application.objects.filter(job=job).order_by('-applied_on')

    return render(request, 'home/job_applicants.html', {
        'user': user,
        'job': job,
        'applicants': applicants
    })

# -----------------------------
# Update Applicant Status
# -----------------------------
@login_required
@require_POST
def update_applicant_status(request, job_id, applicant_id):
    user = request.user
    if user.role != 'employer':
        messages.error(request, "Unauthorized access.")
        return redirect('login')

    job = get_object_or_404(Job, id=job_id, posted_by=user)
    application = get_object_or_404(Application, id=applicant_id, job=job)

    new_status = request.POST.get('status')
    if new_status in ['applied', 'reviewed', 'shortlisted', 'selected', 'rejected']:
        application.status = new_status
        application.save()
        messages.success(request, f"{application.applicant.first_name}'s status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status update.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# -----------------------------
# Edit Profiles
# -----------------------------
@login_required
def edit_student_profile(request):
    user = request.user
    if user.role != 'student':
        messages.error(request, "Unauthorized access.")
        return redirect('welcome')

    if request.method == 'POST':
        user.first_name = request.POST.get('fullname')
        user.roll_number = request.POST.get('roll')
        user.department = request.POST.get('department')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES['profile_pic']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('student_dashboard')

    return render(request, 'home/edit_student_profile.html', {'user': user})

@login_required
def edit_employer_profile(request):
    user = request.user
    if user.role != 'employer':
        messages.error(request, "Unauthorized access.")
        return redirect('welcome')

    if request.method == 'POST':
        user.company_name = request.POST.get('company_name')
        user.hr_name = request.POST.get('hr_name')
        user.industry = request.POST.get('industry')
        user.website = request.POST.get('website')
        user.description = request.POST.get('description')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        if request.FILES.get('profile_pic'):
            user.profile_pic = request.FILES['profile_pic']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('employer_dashboard')

    return render(request, 'home/edit_employer_profile.html', {'user': user})

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Optional: allow only the user who posted the job to delete it
    if job.posted_by != request.user:
        messages.error(request, "You are not allowed to delete this job.")
        return redirect('employer_dashboard')

    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('employer_dashboard')
