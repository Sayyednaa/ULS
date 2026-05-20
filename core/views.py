from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from .forms import CompanyRegistrationForm
from .models import Company, Profile

def home_view(request):
    """
    Root URL view: 
    - If logged in, redirect to the appropriate portal.
    - If not logged in, show the landing page.
    """
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if role in ['admin', 'superadmin']:
            return redirect('admin_dashboard')
        elif role == 'manager':
            return redirect('manager_dashboard')
        elif role == 'employee':
            return redirect('employee_dashboard')
        elif role == 'accountant':
            return redirect('accountant_dashboard')
        elif role == 'driver':
            return redirect('driver_dashboard')
    
    return render(request, 'landing.html')

def access_denied(request):
    return render(request, 'auth/access_denied.html')

def register_company(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create company with logo and currency
                    company = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        logo=form.cleaned_data['logo'],
                        currency=form.cleaned_data['currency']
                    )
                    
                    # Create superadmin user
                    user = Profile.objects.create_user(
                        username=form.cleaned_data['email'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password1'],
                        company=company,
                        role='superadmin'
                    )
                    
                    # Log the user in
                    login(request, user, backend='core.backends.EmailBackend')
                    return redirect('home')
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})
