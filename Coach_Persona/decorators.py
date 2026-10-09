# coaches/decorators.py ACCESS CONTROL DECORATORS
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import CoachProfile

def athlete_data_access_required(view_func):
    """Enforces the trust boundary: requires approved status and claimed program."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            profile = request.user.coach_profile
        except CoachProfile.DoesNotExist:
            raise PermissionDenied("User is not a coach.")

        if profile.status == CoachProfile.Status.FLAGGED_FOR_REVIEW:
            return redirect('onboarding_pending')
        elif profile.status == CoachProfile.Status.REJECTED:
            return redirect('onboarding_rejected')

        if not profile.program_claim:
            return redirect('select_program')

        if not profile.completed_first_run_tour:
            return redirect('first_run_tour')

        return view_func(request, *args, **kwargs)
    return _wrapped_view