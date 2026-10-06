from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from transfer_project import ProfileModifications, AthleteProfiles
from transfer_project import EligibilityLogic

def register(request):
    if request.method == 'POST':
        form = ProfileModifications(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = ProfileModifications()
    return render(request, 'transfers/register.html', {'form': form})

@login_required
def dashboard(request):
    profile = request.user.athlete_profile
    evaluation = EligibilityLogic(profile)
    return render(request, 'transfers/dashboard.html', {
        'profile': profile,
        'evaluation': evaluation
    })

@login_required
def edit_profile(request):
    profile = request.user.athlete_profile
    if request.method == 'POST':
        form = AthleteProfiles(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AthleteProfiles(instance=profile)
    return render(request, 'transfers/edit_profile.html', {'form': form})

def api_architecture(request):
    apis = [
        {
            "name": "College Scorecard API",
            "provider": "Data.gov",
            "cost": "Free (Public key)",
            "use_case": "Directory of accredited 4-year institutions, IPEDS ID, and tuition metrics."
        },
        {
            "name": "CollegeFootballData API",
            "provider": "CFBD",
            "cost": "Free (Bearer token)",
            "use_case": "Division mapping (DI FBS/FCS, DII, DIII) and conference alignments."
        },
        {
            "name": "Transferology / TES",
            "provider": "CollegeSource",
            "cost": "Institutional License",
            "use_case": "Course-to-course transfer equivalency and major-specific prerequisite matches."
        }
    ]
    return render(request, 'transfers/api_architecture.html', {'apis': apis})