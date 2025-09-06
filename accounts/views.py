from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from .forms import RegistrationForm, ProfileEditForm

User = get_user_model()

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Automatically activate account
            user.save()
            
            # Automatically log in the user after successful registration
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created successfully.')
            return redirect('homepage:homepage')  # Redirect to homepage
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, "accounts/register.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('homepage:homepage')  # Redirect to homepage
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please provide both email and password.')
    
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect("accounts:login")

@login_required
def profile_view(request):
    """View user profile with projects and donations"""
    user = request.user
    
    # Get user's created projects
    from crowdfunding_projects.models import Project
    projects = Project.objects.filter(
        creator=user
    ).select_related('category').prefetch_related('tags', 'images').order_by('-created_at')
    
    # Get user's donations
    from crowdfunding_projects.models import Donation
    donations = Donation.objects.filter(
        user=user
    ).select_related('project').order_by('-created_at')
    
    # Calculate statistics
    total_donated = sum(donation.amount for donation in donations)
    total_projects_created = projects.count()
    total_donations_made = donations.count()
    
    context = {
        'user': user,
        'projects': projects,
        'donations': donations,
        'total_donated': total_donated,
        'total_projects_created': total_projects_created,
        'total_donations_made': total_donations_made,
    }
    
    return render(request, "accounts/profile.html", context)

@login_required
def edit_profile(request):
    """Edit user profile information"""
    user = request.user
    
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, "accounts/edit_profile.html", context)

@login_required
@require_POST
def delete_account(request):
    """Delete user account with password confirmation"""
    user = request.user
    password = request.POST.get('password')
    confirm_delete = request.POST.get('confirm_delete')
    
    if confirm_delete == 'true':
        if not password:
            messages.error(request, 'Please enter your password to confirm account deletion.')
            return redirect('accounts:profile')
        
        # Verify password
        if not user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('accounts:profile')
        
        # Logout user first
        logout(request)
        
        # Delete user account
        user.delete()
        
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('accounts:register')
    else:
        messages.error(request, 'Account deletion cancelled.')
        return redirect('accounts:profile')
