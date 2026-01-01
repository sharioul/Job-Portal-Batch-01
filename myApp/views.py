from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone

from .models import *

# ==========================================
# Authentication & User Management Views
# ==========================================

def signupPage(request):
    """Handles user registration."""
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')
        
        if password == confirm_password:
            try:
                user = Custom_User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    user_type=user_type,
                )
                messages.success(request, "Account created successfully.")
                return redirect("signinPage")
            except Exception as e:
                messages.error(request, f"Error creating account: {e}")
        else:
            messages.warning(request, "Passwords do not match.")

    return render(request, 'Common/signup.html')


def signinPage(request):
    """Handles user login."""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("JobFeed")
        else:
            messages.warning(request, "Invalid username or password.")
            
    return render(request, 'Common/login.html')


def logoutPage(request):
    """Handles user logout."""
    logout(request)
    return redirect('signinPage')


@login_required
def changePasswordPage(request):
    """Allows users to change their password."""
    current_user = request.user
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')
        
        if check_password(old_password, request.user.password):
            if newPassword == confirmPassword:
                current_user.set_password(newPassword)
                current_user.save()
                update_session_auth_hash(request, current_user)
                messages.success(request, "Password Changed successfully.")
            else:
                messages.warning(request, "New passwords do not match.")
        else:
            messages.warning(request, "Incorrect old password.")
    
    return render(request, "Common/changePasswordPage.html")


# ==========================================
# Job Management Views (Recruiter)
# ==========================================

@login_required
def addJobPage(request):
    """Allows recruiters to post a new job."""
    current_user = request.user
    if current_user.user_type == "recruiter":
        if request.method == "POST":
            job = JobModel()
            job.user = current_user
            job.job_title = request.POST.get("job_title")
            job.company_name = request.POST.get("company_name")
            job.location = request.POST.get("location")
            job.description = request.POST.get("description")
            job.salary = request.POST.get("salary")
            job.employment_type = request.POST.get("employment_type")
            
            # FIXED: Correctly assign application_deadline instead of overwriting posted_date
            job.application_deadline = request.POST.get("application_deadline")
            
            job.save()
            messages.success(request, "Job Created Successfully")
            return redirect("JobFeed")
        return render(request, 'myAdmin/addJobPage.html')
    else:
        messages.warning(request, "You are not a Recruiter")
        return redirect('JobFeed')


@login_required
def createdJob(request):
    """Displays jobs created by the current recruiter."""
    current_user = request.user
    
    if current_user.user_type == "recruiter":
        jobs = JobModel.objects.filter(user=current_user)
    else:
        jobs = JobModel.objects.none()
        messages.warning(request, "You are not authorized to view this page.")
    
    context = {
        "jobs": jobs
    }
    return render(request, "myAdmin/createdJob.html", context)


@login_required
def editJob(request, edit_id):
    """Allows recruiters to edit an existing job."""
    job = get_object_or_404(JobModel, id=edit_id)
    current_user = request.user
    
    if current_user.user_type == "recruiter":
        # Ensure the recruiter owns the job
        if job.user != current_user:
             messages.warning(request, "You cannot edit a job you didn't create.")
             return redirect("createdJob")

        if request.method == "POST":
            # Update fields
            job.job_title = request.POST.get("job_title")
            job.company_name = request.POST.get("company_name")
            job.location = request.POST.get("location")
            job.description = request.POST.get("description")
            job.salary = request.POST.get("salary")
            job.employment_type = request.POST.get("employment_type")
            
            # FIXED: Correctly assign application_deadline
            job.application_deadline = request.POST.get("application_deadline")
            
            job.save()
            messages.success(request, "Job Updated Successfully")
            return redirect("createdJob")
    else:
        messages.warning(request, "You are not a Recruiter")
        return redirect('JobFeed')
    
    context = {
        "Job": job
    }
    return render(request, "myAdmin/EditJobPage.html", context)


@login_required
def deleteJob(request, delete_id):
    """Allows recruiters to delete a job."""
    job = get_object_or_404(JobModel, id=delete_id)
    if request.user == job.user:
        job.delete()
        messages.success(request, "Job deleted successfully.")
    else:
        messages.warning(request, "You are not authorized to delete this job.")
    return redirect("createdJob")


@login_required
def applicantList(request, job_id):
    """Displays list of applicants for a specific job."""
    job = get_object_or_404(JobModel, id=job_id)
    # Ensure current user is the owner of the job
    if request.user != job.user:
        messages.warning(request, "Access Denied.")
        return redirect('createdJob')

    applications = jobApplyModel.objects.filter(job=job)

    context = {
        'job': job,
        'applications': applications
    }
    return render(request, "myAdmin/applicantList.html", context)


@login_required
def callForInterview(request, job_id, application_id):
    """Updates application status to 'interview_scheduled'."""
    application = get_object_or_404(jobApplyModel, id=application_id)
    # Verify ownership
    if request.user != application.job.user:
        messages.warning(request, "Access Denied.")
        return redirect('JobFeed')

    application.status = 'interview_scheduled'  
    application.save()

    messages.success(request, 'The applicant has been called for an interview.')
    return redirect('applicantList', job_id=job_id)


@login_required
def rejectApplication(request, job_id, application_id):
    """Updates application status to 'rejected'."""
    application = get_object_or_404(jobApplyModel, id=application_id)
    if request.user != application.job.user:
        messages.warning(request, "Access Denied.")
        return redirect('JobFeed')

    application.status = 'rejected'  
    application.save()

    messages.success(request, 'The application has been rejected.')
    return redirect('applicantList', job_id=job_id)


# ==========================================
# Job Search & Viewing Views (Public/Seeker)
# ==========================================

@login_required
def JobFeed(request):
    """Displays the main job feed."""
    jobs = JobModel.objects.all().order_by('-id') # Show newest first
    context = {
        'jobs': jobs
    }
    return render(request, "Common/JobFeed.html", context)


def searchJob(request):
    """Handles job search functionality."""
    query = request.GET.get('query')
    
    if query:
        jobs = JobModel.objects.filter(Q(job_title__icontains=query) 
                                       |Q(description__icontains=query) 
                                       |Q(employment_type__icontains=query) 
                                       |Q(company_name__icontains=query))
    else:
        jobs = JobModel.objects.all()
        
    context = {
        'jobs': jobs,
        'query': query
    }
    return render(request, "Common/search.html", context)


@login_required
def viewJob(request, view_id):
    """Displays details of a single job."""
    job = get_object_or_404(JobModel, id=view_id)
    context = {
        "job": job
    }
    return render(request, "Common/viewJob.html", context)


@login_required      
def ApplyNow(request, job_title, apply_id):
    """Handles job application submission."""
    current_user = request.user
    
    if current_user.user_type == 'jobseeker':
        specific_job = get_object_or_404(JobModel, id=apply_id)
        already_exists = jobApplyModel.objects.filter(user=current_user, job=specific_job).exists()
        
        context = {
            'specific_job': specific_job,
            'already_exists': already_exists
        }
        
        if request.method == 'POST':
            Full_Name = request.POST.get("Full_Name")
            Work_Experience = request.POST.get("Work_Experience")
            Skills = request.POST.get("Skills")
            Linkedin_URL = request.POST.get("Linkedin_URL")
            Expected_Salary = request.POST.get("Expected_Salary")
            Resume = request.FILES.get("Resume")
            Cover = request.POST.get("Cover")
            
            apply = jobApplyModel(
                user=current_user,
                job=specific_job,
                Resume=Resume,
                Full_Name=Full_Name,
                Work_Experience=Work_Experience,
                Skills=Skills,
                Expected_Salary=Expected_Salary,
                Linkedin_URL=Linkedin_URL,
                Cover=Cover,
                status="pending"
            )
            apply.save()
            messages.success(request, "Applied successfully!")
            return redirect("JobFeed")
            
        return render(request, "Seeker/applynow.html", context)
    else:
        messages.warning(request, "You are not a Job Seeker")
        return redirect("JobFeed")


@login_required
def appliedJob(request):
    """Displays jobs the user has applied to."""
    current_user = request.user

    # Get all job applications for the current user
    job_applications = jobApplyModel.objects.filter(user=current_user)

    job_messages = {}
    for job_application in job_applications:
        msgs = MessageModel.objects.filter(application=job_application)
        job_messages[job_application.id] = msgs

    context = {
        "Job": job_applications,
        "job_messages": job_messages, 
    }
    return render(request, "Seeker/appliedJob.html", context)


# ==========================================
# Messaging System
# ==========================================

@login_required
def message_list(request, job_id):
    """Displays messages for a specific job application (Recruiter view)."""
    job = get_object_or_404(JobModel, id=job_id)
    messages_list = MessageModel.objects.filter(application__job=job)

    context = {
        'job': job,
        'messages': messages_list
    }
    return render(request, 'myAdmin/message_list.html', context)


@login_required
def send_message(request, job_id, application_id):
    """Sends a message to an applicant."""
    current_user = request.user
    job = get_object_or_404(JobModel, id=job_id)
    application = get_object_or_404(jobApplyModel, id=application_id)

    context = {
        'job': job,
        'application': application
    }

    if request.method == 'POST':
        content = request.POST.get('messageText')
        recipient = application.user

        # Check for duplicate messages
        if MessageModel.objects.filter(
            application=application,
            sender=current_user,
            content=content,
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=1)  # Check if sent within the last minute
        ).exists():
            messages.error(request, 'You have already sent this message. Duplicate messages are not allowed.')
            return redirect('message_list', job_id=job_id)

        # If no duplicate, save the message
        message = MessageModel(
            application=application,
            sender=current_user,
            recipient=recipient,
            content=content,
            timestamp=timezone.now()
        )
        message.save()

        messages.success(request, 'Message sent successfully!')
        return redirect('message_list', job_id=job_id)

    else:
        return render(request, 'myAdmin/send_message.html', context)


@login_required
def viewMessage(request, viewMessage_id):
    """Displays messages for a specific application (Seeker view)."""
    application = get_object_or_404(jobApplyModel, id=viewMessage_id)
    
    msgs = MessageModel.objects.filter(application=application).order_by('timestamp')
    
    context = {
        'application': application,
        'messages': msgs
    }
    return render(request, "Seeker/viewMessage.html", context)


@login_required
def myMessages(request):
    """Displays all messages for the current user."""
    # Get all messages where the logged-in user is the recipient
    msgs = MessageModel.objects.filter(recipient=request.user).order_by('-timestamp')

    # Create a set to hold job applications linked to the messages
    applications = set()

    for message in msgs:
        applications.add(message.application)

    # Check if any applications have been rejected or selected for interview
    rejected_apps = [app for app in applications if app.status == 'rejected']
    selected_apps = [app for app in applications if app.status == 'interview_scheduled'] 

    context = {
        'messages': msgs,
        'rejected_apps': rejected_apps, 
        'interviewed_apps': selected_apps, 
    }
    return render(request, 'Common/myMessages.html', context)


# ==========================================
# User Profile & Settings
# ==========================================

@login_required
def createBasicInfo(request):
    """Updates basic user profile information."""
    if request.user.user_type == 'jobseeker' or request.user.user_type == 'recruiter' :
        current_user = request.user
        
        try:
            info = BasicInfoModel.objects.get(user=current_user)
        except BasicInfoModel.DoesNotExist:
            info = None

        if request.method == 'POST':
            resume, created = BasicInfoModel.objects.get_or_create(user=current_user)
            
            resume.contact_No = request.POST.get("contact_No")
            resume.Designation = request.POST.get("Designation")
            if request.FILES.get("Profile_Pic"):
                resume.Profile_Pic = request.FILES.get("Profile_Pic")
            
            resume.Carrer_Summary = request.POST.get("Carrer_Summary")
            resume.Age = request.POST.get("Age")
            resume.Gender = request.POST.get("Gender")
            resume.save()
            
            current_user.first_name = request.POST.get("first_name")
            current_user.last_name = request.POST.get("second_name")
            current_user.save()
            
            messages.success(request, "Resume updated successfully.")
            return redirect('MySettingsPage')  
        
        return render(request, "Common/createBasicInfo.html", {'info': info})
    elif request.user.user_type == 'admin':
        messages.warning(request, "You are not authorized to access this page.")
        return redirect('MySettingsPage')
    
    # Fallback for any other case
    return render(request, "Common/createBasicInfo.html")


@login_required
def profile_view(request):
    """Displays the user's full profile."""
    current_user = request.user

    try:
        information = get_object_or_404(BasicInfoModel, user=current_user)
    except Http404:
        messages.warning(request, "You don't have a resume. Please create one.")
        return redirect('createBasicInfo') 

    languages = LanguageModel.objects.filter(user=current_user)
    skills = SkillModel.objects.filter(user=current_user)
    education = EducationModel.objects.filter(user=current_user)
    interests = InterestModel.objects.filter(user=current_user)
    experiences = ExperienceModel.objects.filter(user=current_user)

    context = {
        'Information': information,
        'Languages': languages,
        'Skills': skills,
        'Education': education,
        'Interests': interests,
        'Experiences': experiences,
    }
    
    return render(request, "Common/profilePage.html", context)


@login_required
def MySettingsPage(request):
    """Displays the settings page with user details."""
    current_user = request.user
    
    myLanguage = LanguageModel.objects.filter(user=current_user)
    mySkill = SkillModel.objects.filter(user=current_user)
    myEducation = EducationModel.objects.filter(user=current_user)
    myInterest = InterestModel.objects.filter(user=current_user)
    myExperience = ExperienceModel.objects.filter(user=current_user)
    
    context = {
        "myLanguage": myLanguage,
        "mySkill": mySkill,
        "myInterest": myInterest,
        'myEducation': myEducation,
        "myExperience": myExperience
    }
    return render(request, "Common/MySettingsPage.html", context)


@login_required
def addLanguage(request):
    """Allows jobseekers to add a language."""
    if request.user.user_type != 'jobseeker':
        messages.warning(request, "You are not authorized to add languages.")
        return redirect('MySettingsPage')

    all_lan = IntermediateLanguageModel.objects.all()
    current_user = request.user

    if request.method == 'POST':
        Language_Id = request.POST.get("Language_Id")
        Proficiency_Level = request.POST.get("Proficiency_Level")

        if not Language_Id or not Proficiency_Level:
            messages.warning(request, "Both language and proficiency level are required.")
            return render(request, "myAdmin/addLanguage.html", {'all_lan': all_lan})

        MyObj = get_object_or_404(IntermediateLanguageModel, id=Language_Id)

        if LanguageModel.objects.filter(user=current_user, Language_Name=MyObj.Language_Name).exists():
            messages.warning(request, "This language already exists in your profile.")
            return render(request, "myAdmin/addLanguage.html", {'all_lan': all_lan})

        LanguageModel.objects.create(
            user=current_user,
            Language_Name=MyObj.Language_Name,
            Proficiency_Level=Proficiency_Level,
        )
        messages.success(request, "Language added successfully.")
        return redirect("MySettingsPage")

    context = {
        "all_lan": all_lan
    }
    return render(request, "myAdmin/addLanguage.html", context)


@login_required
def addSkillPage(request):
    """Allows jobseekers to add a skill."""
    if request.user.user_type != 'jobseeker':
        messages.warning(request, "You are not authorized to add skills.")
        return redirect('MySettingsPage')

    All_Skill = IntermediateSkillModel.objects.all()
    current_user = request.user

    if request.method == 'POST':
        Skill_Id = request.POST.get("Skill_Id")
        Skill_Level = request.POST.get("Skill_Level")

        MyObj = get_object_or_404(IntermediateSkillModel, id=Skill_Id)

        if SkillModel.objects.filter(user=current_user, Skill_Name=MyObj.My_Skill_Name).exists():
            messages.warning(request, "Skill already exists.")
        else:
            SkillModel.objects.create(
                user=current_user,
                Skill_Name=MyObj.My_Skill_Name,
                Skill_Level=Skill_Level,
            )
            messages.success(request, "Skill added successfully.")
            return redirect("MySettingsPage")

    context = {
        "All_Skill": All_Skill
    }
    return render(request, "myAdmin/addSkill.html", context)


@login_required
def add_education(request):
    """Allows jobseekers to add education details."""
    if request.user.user_type != 'jobseeker':
        messages.warning(request, "You are not authorized to add education information.")
        return redirect('MySettingsPage')

    institutes = InstituteNameModel.objects.all()
    degrees = DegreeModel.objects.all()
    fields_of_study = FieldOfStudyModel.objects.all()

    if request.method == 'POST':
        institution_name = request.POST.get('institution_name')
        degree_name = request.POST.get('degree_name')
        field_of_study_name = request.POST.get('field_of_study')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        EducationModel.objects.create(
            user=request.user,
            institution_name=institution_name,
            degree=degree_name,
            field_of_study=field_of_study_name,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, "Education added successfully.")
        return redirect('MySettingsPage')
    
    context={
        'institutes': institutes,
        'degrees': degrees,
        'fields_of_study': fields_of_study
    }
    return render(request, 'myAdmin/addEducation.html', context)


@login_required
def add_interest(request):
    """Allows jobseekers to add interests."""
    if request.user.user_type != 'jobseeker':
        messages.warning(request, "You are not authorized to add interests.")
        return redirect('MySettingsPage')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name or not description:
            messages.warning(request, "Both name and description are required.")
            return render(request, 'add_interest.html')

        InterestModel.objects.create(
            user=request.user, 
            name=name,
            description=description
        )
        messages.success(request, "Interest added successfully.")
        return redirect('MySettingsPage')

    return render(request, 'myAdmin/addInterest.html')


@login_required
def add_experience(request):
    """Allows jobseekers to add work experience."""
    if request.user.user_type != 'jobseeker':
        messages.warning(request, "You are not authorized to add experience.")
        return redirect('MySettingsPage')

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        company_name = request.POST.get('company_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        if not job_title or not company_name or not start_date:
            messages.warning(request, "Job title, company name, and start date are required.")
            return render(request, 'add_experience.html')

        ExperienceModel.objects.create(
            user=request.user,
            job_title=job_title,
            company_name=company_name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        messages.success(request, "Experience added successfully.")
        return redirect('MySettingsPage')

    return render(request, 'myAdmin/addExperience.html')


@login_required
def delete_language(request, id):
    """Deletes a language entry."""
    language = get_object_or_404(LanguageModel, id=id)
    # Security check: ensure user owns the object
    if language.user == request.user:
        language.delete()
        messages.success(request, "Language deleted successfully.")
    else:
        messages.warning(request, "Unauthorized action.")
    return redirect('MySettingsPage')


@login_required
def delete_skill(request, id):
    """Deletes a skill entry."""
    skill = get_object_or_404(SkillModel, id=id)
    if skill.user == request.user:
        skill.delete()
        messages.success(request, "Skill deleted successfully.")
    else:
        messages.warning(request, "Unauthorized action.")
    return redirect('MySettingsPage')


@login_required
def delete_interest(request, id):
    """Deletes an interest entry."""
    interest = get_object_or_404(InterestModel, id=id)
    if interest.user == request.user:
        interest.delete()
        messages.success(request, "Interest deleted successfully.")
    else:
        messages.warning(request, "Unauthorized action.")
    return redirect('MySettingsPage')


@login_required
def delete_education(request, id):
    """Deletes an education entry."""
    education = get_object_or_404(EducationModel, id=id)
    if education.user == request.user:
        education.delete()
        messages.success(request, "Education deleted successfully.")
    else:
        messages.warning(request, "Unauthorized action.")
    return redirect('MySettingsPage')


@login_required
def delete_experience(request, id):
    """Deletes an experience entry."""
    experience = get_object_or_404(ExperienceModel, id=id)
    if experience.user == request.user:
        experience.delete()
        messages.success(request, "Experience deleted successfully.")
    else:
        messages.warning(request, "Unauthorized action.")
    return redirect('MySettingsPage')
