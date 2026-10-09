# coaches/services.py TRUST EVALUATION ENGINE
from django.core.mail import send_mail
from django.db import transaction
from django.conf import settings
from .models import CoachProfile, Institution, Program

class CoachOnboardingService:
    @staticmethod
    @transaction.atomic
    def process_institution_selection(coach_profile: CoachProfile, institution: Institution):
        """
        Executes the trust boundary decision tree:
        1. Checks domain match against institution's verified domains.
        2. Checks if an active admin already exists.
        3. Assigns either AUTO_APPROVED or FLAGGED_FOR_REVIEW.
        """
        coach_profile.institution = institution
        email_domain = coach_profile.email_domain

        # Verification check
        domain_matches = institution.verified_domains.filter(domain=email_domain).exists()
        has_admin = institution.has_active_admin()

        if not domain_matches:
            coach_profile.status = CoachProfile.Status.FLAGGED_FOR_REVIEW
            coach_profile.review_reason = f"Email domain '@{email_domain}' does not match verified domains."
            coach_profile.save()
            CoachOnboardingService.notify_platform_admins(coach_profile)

        elif not has_admin:
            # Domain matches, but first account for this institution
            coach_profile.status = CoachProfile.Status.FLAGGED_FOR_REVIEW
            coach_profile.review_reason = "Initial bootstrap account for institution: requires identity verification."
            coach_profile.save()
            CoachOnboardingService.notify_platform_admins(coach_profile)

        else:
            # Domain matches and institution already has a verified admin
            coach_profile.status = CoachProfile.Status.APPROVED
            coach_profile.review_reason = "Auto-approved: domain matched and institution admin active."
            coach_profile.save()
            CoachOnboardingService.notify_institution_admins(coach_profile)

        return coach_profile

    @staticmethod
    def notify_institution_admins(new_coach_profile: CoachProfile):
        admin_emails = new_coach_profile.institution.get_institution_admin_emails()
        if not admin_emails:
            return

        send_mail(
            subject=f"New Coach Joined: {new_coach_profile.user.get_full_name()}",
            message=(
                f"{new_coach_profile.user.get_full_name()} ({new_coach_profile.user.email}) "
                f"was auto-approved using your institution's verified domain."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=True,
        )

    @staticmethod
    def notify_platform_admins(flagged_coach: CoachProfile):
        send_mail(
            subject=f"[Manual Review Required] Coach Signup: {flagged_coach.user.email}",
            message=(
                f"Coach: {flagged_coach.user.get_full_name()} ({flagged_coach.user.email})\n"
                f"Claimed Institution: {flagged_coach.institution.name}\n"
                f"Flag Reason: {flagged_coach.review_reason}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.PLATFORM_ADMIN_EMAIL],
            fail_silently=True,
        )

    @staticmethod
    @transaction.atomic
    def admin_approve_coach(coach_profile: CoachProfile, make_institution_admin: bool = False):
        coach_profile.status = CoachProfile.Status.APPROVED
        if make_institution_admin or not coach_profile.institution.has_active_admin():
            coach_profile.is_institution_admin = True
        coach_profile.review_reason = "Manually approved by platform admin."
        coach_profile.save()

    @staticmethod
    @transaction.atomic
    def admin_reject_coach(coach_profile: CoachProfile, reason: str = ""):
        coach_profile.status = CoachProfile.Status.REJECTED
        coach_profile.review_reason = reason or "Rejected during manual review."
        coach_profile.save()