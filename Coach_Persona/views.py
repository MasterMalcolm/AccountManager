# coaches/views.py VIEWS & NAVIGATION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .models import CoachProfile
from .forms import CoachSignUpForm, InstitutionSelectForm, ProgramClaimForm
from .services import CoachOnboardingService
from .decorators import athlete_data_access_required

def signup_coach(request):
    if request.method == 'POST':
        form = CoachSignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            # Create the associated pending CoachProfile
            CoachProfile.objects.create(user=user)
            login(request, user)
            return redirect('select_institution')
    else:
        form = CoachSignUpForm()
    return render(request, 'coaches/signup.html', {'form': form})

@login_required
def select_institution(request):
    profile = request.user.coach_profile
    if profile.institution:
        return redirect('onboarding_hub')

    if request.method == 'POST':
        form = InstitutionSelectForm(request.POST)
        if form.is_valid():
            institution = form.cleaned_data['institution']
            CoachOnboardingService.process_institution_selection(profile, institution)
            return redirect('onboarding_hub')
    else:
        form = InstitutionSelectForm()
    return render(request, 'coaches/select_institution.html', {'form': form})

@login_required
def onboarding_hub(request):
    """Directs the user to the correct onboarding step based on their status."""
    profile = request.user.coach_profile

    if not profile.institution:
        return redirect('select_institution')
    if profile.status == CoachProfile.Status.FLAGGED_FOR_REVIEW:
        return render(request, 'coaches/pending_review.html', {'profile': profile})
    if profile.status == CoachProfile.Status.REJECTED:
        return render(request, 'coaches/rejected.html', {'profile': profile})
    if not profile.program_claim:
        return redirect('select_program')
    if not profile.completed_first_run_tour:
        return redirect('first_run_tour')

    return redirect('athlete_directory')

@login_required
def select_program(request):
    profile = request.user.coach_profile
    if profile.status != CoachProfile.Status.APPROVED:
        return redirect('onboarding_hub')

    if request.method == 'POST':
        form = ProgramClaimForm(request.POST, institution=profile.institution)
        if form.is_valid():
            profile.program_claim = form.cleaned_data['program']
            profile.save(update_fields=['program_claim'])
            return redirect('first_run_tour')
    else:
        form = ProgramClaimForm(institution=profile.institution)
    return render(request, 'coaches/select_program.html', {'form': form, 'institution': profile.institution})

@login_required
def first_run_tour(request):
    profile = request.user.coach_profile
    if profile.status != CoachProfile.Status.APPROVED or not profile.program_claim:
        return redirect('onboarding_hub')

    if request.method == 'POST':
        profile.completed_first_run_tour = True
        profile.save(update_fields=['completed_first_run_tour'])
        return redirect('athlete_directory')

    return render(request, 'coaches/first_run_tour.html', {'profile': profile})

@login_required
@athlete_data_access_required
def athlete_directory(request):
    """Protected athlete search and profile index."""
    return render(request, 'coaches/athlete_directory.html', {
        'profile': request.user.coach_profile,
        'program': request.user.coach_profile.program_claim
    })

# --- Platform Admin Moderation Actions ---
@user_passes_test(lambda u: u.is_superuser)
def manual_review_queue(request):
    pending_coaches = CoachProfile.objects.filter(
        status=CoachProfile.Status.FLAGGED_FOR_REVIEW
    ).select_related('user', 'institution')
    return render(request, 'coaches/admin_queue.html', {'coaches': pending_coaches})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def approve_coach_action(request, profile_id):
    profile = get_object_or_404(CoachProfile, id=profile_id)
    make_admin = request.POST.get('is_institution_admin') == 'true'
    CoachOnboardingService.admin_approve_coach(profile, make_institution_admin=make_admin)
    return redirect('manual_review_queue')

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def reject_coach_action(request, profile_id):
    profile = get_object_or_404(CoachProfile, id=profile_id)
    reason = request.POST.get('rejection_reason', 'Domain mismatch or unverified identity.')
    CoachOnboardingService.admin_reject_coach(profile, reason=reason)
    return redirect('manual_review_queue')