from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from transfer_project import AthleteProfiles

@receiver(post_save, sender=User)
def create_or_save_athlete_profile(sender, instance, created, **kwargs):
    if created:
        AthleteProfiles.objects.create(
            user=instance,
            current_school_name="Default 4-Year University"
        )
    instance.athlete_profile.save()