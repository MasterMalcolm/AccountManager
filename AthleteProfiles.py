from django.db import models
from django.contrib.auth.models import User

class Division(models.TextChoices):
    DI = 'DI', 'NCAA Division I'
    DII = 'DII', 'NCAA Division II'
    DIII = 'DIII', 'NCAA Division III'
    NAIA = 'NAIA', 'NAIA'
    OTHER = 'OTHER', 'Other 4-Year (USCAA/NCCAA)'

class AthleteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_profile')
    sport = models.CharField(max_length=100, default='General/Other')
    current_school_name = models.CharField(max_length=255)
    current_division = models.CharField(max_length=10, choices=Division.choices, default=Division.DI)
    target_division = models.CharField(max_length=10, choices=Division.choices, default=Division.DI)
    
    # Eligibility & Academic Factors
    in_good_standing = models.BooleanField(
        default=True,
        help_text="In good academic and disciplinary standing with no active suspensions."
    )
    academically_eligible_prior = models.BooleanField(
        default=True,
        help_text="Would have been academically eligible had you stayed at current school."
    )
    last_term_credit_hours = models.PositiveIntegerField(
        default=12,
        help_text="Passed credits in last full-time term (relevant for DII / NAIA)."
    )
    entered_portal_during_window = models.BooleanField(
        default=True,
        help_text="Entered transfer portal within sport-specific window (DI requirement)."
    )
    competed_same_championship_season = models.BooleanField(
        default=False,
        help_text="Already competed for current institution in same championship season."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.current_school_name} -> {self.target_division})"