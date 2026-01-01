from django.urls import path
from .views import *

urlpatterns = [
    # Authentication
    path('', signupPage, name='signupPage'),
    path('signinPage/', signinPage, name='signinPage'),
    path('logoutPage/', logoutPage, name='logoutPage'),
    path('changePasswordPage/', changePasswordPage, name='changePasswordPage'),

    # Profile & Settings
    path('createBasicInfo/', createBasicInfo, name="createBasicInfo"),
    path('MySettingsPage/', MySettingsPage, name="MySettingsPage"),
    path('settings/', MySettingsPage, name='MySettingsPage_Alias'), # Alias kept for safety
    path('profile_view/', profile_view, name='profile_view'),

    # Settings - Add/Edit Items
    path('addLanguage/', addLanguage, name="addLanguage"), # Corrected name
    path('addSkillPage/', addSkillPage, name="addSkillPage"),
    path('add_education/', add_education, name="add_education"),
    path('add_interest/', add_interest, name="add_interest"),
    path('add-experience/', add_experience, name='add_experience'),

    # Settings - Delete Items
    path('delete_language/<int:id>/', delete_language, name='delete_language'),
    path('delete_skill/<int:id>/', delete_skill, name='delete_skill'),
    path('delete_interest/<int:id>/', delete_interest, name='delete_interest'),
    path('delete_education/<int:id>/', delete_education, name='delete_education'),
    path('delete_experience/<int:id>/', delete_experience, name='delete_experience'),

    # Job Management (Recruiter)
    path('addJobPage/', addJobPage, name='addJobPage'),
    path('createdJob/', createdJob, name='createdJob'),
    path('editJob/<int:edit_id>/', editJob, name='editJob'),
    path('deleteJob/<int:delete_id>/', deleteJob, name='deleteJob'),
    path('applicantList/<int:job_id>/', applicantList, name='applicantList'),
    path('job/<int:job_id>/applicants/<int:application_id>/interview/', callForInterview, name='call_for_interview'),
    path('job/<int:job_id>/applicants/<int:application_id>/reject/', rejectApplication, name='reject_application'),
    
    # Job Viewing & Searching (Public/Seeker)
    path('JobFeed/', JobFeed, name='JobFeed'),
    path('searchJob/', searchJob, name='searchJob'),
    path('viewJob/<int:view_id>/', viewJob, name='viewJob'),
    path('ApplyNow/<str:job_title>/<int:apply_id>/', ApplyNow, name='ApplyNow'), # apply_id should ideally be int
    path('appliedJob/', appliedJob, name='appliedJob'),

    # Messaging
    path('ApplyNow/viewMessage/<int:viewMessage_id>', viewMessage, name='viewMessage'),
    path('job/<int:job_id>/application/<int:application_id>/send-message/', send_message, name='send_message'),
    path('job/<int:job_id>/messages/', message_list, name='message_list'),
    path('my-messages/', myMessages, name='my_messages'),
]
