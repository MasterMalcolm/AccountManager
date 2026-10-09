# coaches/forms.py FORMS
from django import forms
from django.contrib.auth.models import User
from .models import Institution, Program

class CoachSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'coach@university.edu'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class InstitutionSelectForm(forms.Form):
    institution = forms.ModelChoiceField(
        queryset=Institution.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select your institution"
    )


class ProgramClaimForm(forms.Form):
    program = forms.ModelChoiceField(
        queryset=Program.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select your sport/program"
    )

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution:
            self.fields['program'].queryset = Program.objects.filter(
                institution=institution
            ).select_related('sport').order_by('sport__name')