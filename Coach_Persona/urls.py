# coaches/urls.py URL CONFIGURATION
from django.urls import path
from Coach_Persona import views

urlpatterns = [
    path('signup/', views.signup_coach, name='signup_coach'),
    path('onboarding/', views.onboarding_hub, name='onboarding_hub'),
    path('onboarding/select-institution/', views.select_institution, name='select_institution'),
    path('onboarding/select-program/', views.select_program, name='select_program'),
    path('onboarding/first-run/', views.first_run_tour, name='first_run_tour'),
    path('athletes/', views.athlete_directory, name='athlete_directory'),
    
    # Admin queue
    path('admin/review-queue/', views.manual_review_queue, name='manual_review_queue'),
    path('admin/review-queue/<int:profile_id>/approve/', views.approve_coach_action, name='approve_coach'),
    path('admin/review-queue/<int:profile_id>/reject/', views.reject_coach_action, name='reject_coach'),
]