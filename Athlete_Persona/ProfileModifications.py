from django import forms
from django.contrib.auth.models import User
from Athlete_Persona import AthleteProfiles

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class AthleteProfileForm(forms.ModelForm):
    class Meta:
        model = AthleteProfiles
        fields = [
            'sport',
            'current_school_name',
            'current_division',
            'target_division',
            'in_good_standing',
            'academically_eligible_prior',
            'last_term_credit_hours',
            'entered_portal_during_window',
            'competed_same_championship_season'
        ]
        widgets = {
            'sport': forms.TextInput(attrs={'class': 'form-input'}),
            'current_school_name': forms.TextInput(attrs={'class': 'form-input'}),
            'current_division': forms.Select(attrs={'class': 'form-select'}),
            'target_division': forms.Select(attrs={'class': 'form-select'}),
            'last_term_credit_hours': forms.NumberInput(attrs={'class': 'form-input'}),
        }