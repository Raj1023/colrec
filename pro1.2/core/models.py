from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --------------------------------
# Custom User Model
# --------------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('employer', 'Employer'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # Student fields
    department = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)

    # Employer fields
    company_name = models.CharField(max_length=255, blank=True, null=True)
    hr_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Shared fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


# --------------------------------
# Job Model (Final Merged Version)
# --------------------------------
class Job(models.Model):
    JOB_TYPES = [
        ('full', 'Full-time'),
        ('part', 'Part-time'),
        ('remote', 'Remote'),
        ('intern', 'Internship'),
    ]

    EXPERIENCE_LEVELS = [
        ('0-1', '0-1 Years'),
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5+', '5+ Years'),
    ]

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_LEVELS)
    salary = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Salary in LPA")
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    skills = models.TextField(help_text="Comma-separated list of required skills", blank=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def __str__(self):
        return f"{self.title} at {self.company}"


# --------------------------------
# Application Model
# --------------------------------
class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.applicant.username} → {self.job.title} ({self.status})"


# --------------------------------
# Saved Job Model
# --------------------------------
class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    saved_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


# --------------------------------
# Notification Model
# --------------------------------
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
