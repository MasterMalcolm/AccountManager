# coaches/models.py DATA MODELS
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def has_active_admin(self) -> bool:
        """Returns True if at least one verified institution admin exists."""
        return self.memberships.filter(
            is_institution_admin=True,
            status=CoachProfile.Status.APPROVED
        ).exists()

    def get_institution_admin_emails(self):
        return list(
            self.memberships.filter(
                is_institution_admin=True,
                status=CoachProfile.Status.APPROVED
            ).values_list('user__email', flat=True)
        )

    def __str__(self):
        return self.name


class InstitutionDomain(models.Model):
    """Verified domains belonging to the institution (e.g., 'utexas.edu')."""
    institution = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='verified_domains'
    )
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    is_primary = models.BooleanField(default=False)

    def clean(self):
        self.domain = self.domain.lower().strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.domain} -> {self.institution.name}"


class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'MBB', 'WSOCC'

    def __str__(self):
        return self.name


class Program(models.Model):
    """An athletic program combining an institution and a sport."""
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='programs')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='programs')

    class Meta:
        unique_together = ('institution', 'sport')

    def __str__(self):
        return f"{self.institution.name} - {self.sport.name}"


class CoachProfile(models.Model):
    class Status(models.TextChoices):
        FLAGGED_FOR_REVIEW = 'FLAGGED', _('Flagged for Platform Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    institution = models.ForeignKey(
        Institution, 
        on_delete=models.PROTECT, 
        related_name='memberships',
        null=True,
        blank=True
    )
    program_claim = models.ForeignKey(
        Program, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='coaches'
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.FLAGGED_FOR_REVIEW
    )
    review_reason = models.CharField(max_length=255, blank=True)
    is_institution_admin = models.BooleanField(
        default=False, 
        help_text="Designates this coach as the verified institution admin."
    )
    completed_first_run_tour = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def email_domain(self) -> str:
        if '@' in self.user.email:
            return self.user.email.split('@')[1].lower().strip()
        return ''

    def can_access_athlete_data(self) -> bool:
        return self.status == self.Status.APPROVED and self.program_claim is not None

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.status})"