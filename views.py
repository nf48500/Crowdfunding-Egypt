from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import (
    Project, Category, Tag, Comment, Rating, Donation, Report
)
from .forms import (
    ProjectForm, CommentForm, ReplyForm, RatingForm, 
    DonationForm, ReportForm, ProjectSearchForm
)

User = get_user_model()

def project_list(request):
    """Display list of all approved projects with search and filtering"""
    projects = Project.objects.filter(
        is_approved=True,
        status__in=['active', 'funded']
    ).select_related('category', 'creator').prefetch_related('tags', 'images')
    
    # Search and filtering
    search_form = ProjectSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        search_type = search_form.cleaned_data.get('search_type')
        category = search_form.cleaned_data.get('category')
        min_target = search_form.cleaned_data.get('min_target')
        max_target = search_form.cleaned_data.get('max_target')
        status = search_form.cleaned_data.get('status')
        
        if search_query:
            if search_type == 'title':
                projects = projects.filter(title__icontains=search_query)
            elif search_type == 'tag':
                projects = projects.filter(tags__name__icontains=search_query)
            elif search_type == 'category':
                projects = projects.filter(category__name__icontains=search_query)
            elif search_type == 'creator':
                projects = projects.filter(creator__username__icontains=search_query)
        
        if category:
            projects = projects.filter(category=category)
        
        if min_target:
            projects = projects.filter(total_target__gte=min_target)
        
        if max_target:
            projects = projects.filter(total_target__lte=max_target)
        
        if status:
            projects = projects.filter(status=status)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'rating':
        projects = projects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
    elif sort_by == 'target':
        projects = projects.order_by('-total_target')
    elif sort_by == 'deadline':
        projects = projects.order_by('end_date')
    else:
        projects = projects.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True).annotate(
        project_count=Count('projects', filter=Q(projects__is_approved=True))
    )
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories,
        'sort_by': sort_by,
    }
    
    return render(request, 'crowdfunding_projects/project_list.html', context)

def project_detail(request, slug):
    """Display project details with comments, ratings, and donation form"""
    # Allow creators to view their own pending projects
    project = get_object_or_404(
        Project.objects.select_related('category', 'creator')
        .prefetch_related('tags', 'images', 'comments', 'ratings'),
        slug=slug
    )
    
    # Check if user can view this project
    if not project.is_approved and request.user != project.creator:
        raise Http404("Project not found or not approved yet.")
    
    # Check if user has already rated
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(project=project, user=request.user)
        except Rating.DoesNotExist:
            pass
    
    # Get comments (excluding replies for main list)
    comments = project.comments.filter(parent=None, is_approved=True).select_related('user')
    
    # Get similar projects
    similar_projects = project.get_similar_projects(4)
    
    # Forms
    comment_form = CommentForm()
    rating_form = RatingForm(instance=user_rating)
    donation_form = DonationForm()
    report_form = ReportForm()
    
    context = {
        'project': project,
        'comments': comments,
        'similar_projects': similar_projects,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'donation_form': donation_form,
        'report_form': report_form,
        'user_rating': user_rating,
    }
    
    return render(request, 'crowdfunding_projects/project_detail.html', context)

@login_required
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.status = 'active'  # Auto-approve for development
            project.is_approved = True  # Auto-approve for development
            
            # Generate slug if not present
            if not project.slug:
                import uuid
                project.slug = f"{uuid.uuid4().hex[:8]}-{project.title.lower().replace(' ', '-')}"
            
            project.save()
            # Save many-to-many relationships (tags)
            form.save_m2m()
            
            # Refresh from database to ensure slug is saved
            project.refresh_from_db()
            
            messages.success(
                request, 
                'Project created successfully! Your project is now live and visible on the homepage.'
            )
            return redirect('projects:project_detail', slug=project.slug)
        else:
            # Form is invalid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    
    # Get categories and tags for the form
    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'crowdfunding_projects/project_form.html', context)

@login_required
def project_edit(request, slug):
    """Edit an existing project"""
    project = get_object_or_404(Project, slug=slug, creator=request.user)
    
    if project.status not in ['draft', 'pending']:
        messages.error(request, 'Only draft or pending projects can be edited.')
        return redirect('projects:project_detail', slug=project.slug)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'categories': Category.objects.filter(is_active=True),
        'tags': Tag.objects.all(),
    }
    
    return render(request, 'crowdfunding_projects/project_form.html', context)

@login_required
@require_POST
def project_cancel(request, slug):
    """Cancel a project if funding is less than 25%"""
    project = get_object_or_404(Project, slug=slug, creator=request.user)
    
    if not project.is_cancellable:
        messages.error(request, 'Project cannot be cancelled. It must be active and less than 25% funded.')
        return redirect('projects:project_detail', slug=project.slug)
    
    project.status = 'cancelled'
    project.save()
    
    messages.success(request, 'Project cancelled successfully.')
    return redirect('projects:project_detail', slug=project.slug)

@login_required
@require_POST
def add_comment(request, slug):
    """Add a comment to a project"""
    project = get_object_or_404(Project, slug=slug, is_approved=True)
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.project = project
        comment.user = request.user
        comment.save()
        
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Please correct the errors in your comment.')
    
    return redirect('projects:project_detail', slug=project.slug)

@login_required
@require_POST
def add_reply(request, comment_id):
    """Add a reply to a comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
    
    form = ReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.project = parent_comment.project
        reply.user = request.user
        reply.parent = parent_comment
        reply.save()
        
        messages.success(request, 'Reply added successfully!')
    else:
        messages.error(request, 'Please correct the errors in your reply.')
    
    return redirect('projects:project_detail', slug=parent_comment.project.slug)

@login_required
@require_POST
def add_rating(request, slug):
    """Add or update a rating for a project"""
    project = get_object_or_404(Project, slug=slug, is_approved=True)
    
    form = RatingForm(request.POST)
    if form.is_valid():
        rating, created = Rating.objects.update_or_create(
            project=project,
            user=request.user,
            defaults={
                'rating': form.cleaned_data['rating'],
                'review': form.cleaned_data['review']
            }
        )
        
        if created:
            messages.success(request, 'Rating added successfully!')
        else:
            messages.success(request, 'Rating updated successfully!')
    else:
        messages.error(request, 'Please correct the errors in your rating.')
    
    return redirect('projects:project_detail', slug=project.slug)

@login_required
@require_POST
def add_donation(request, slug):
    """Add a donation to a project"""
    project = get_object_or_404(Project, slug=slug, is_approved=True, status='active')
    
    form = DonationForm(request.POST)
    if form.is_valid():
        donation = form.save(commit=False)
        donation.project = project
        donation.user = request.user
        donation.save()
        
        messages.success(
            request, 
            f'Thank you for your donation of {donation.amount} EGP!'
        )
    else:
        messages.error(request, 'Please correct the errors in your donation.')
    
    return redirect('projects:project_detail', slug=project.slug)

@login_required
@require_POST
def report_content(request, slug):
    """Report inappropriate project or comment content"""
    project = get_object_or_404(Project, slug=slug, is_approved=True)
    
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.report_type = 'project'
        report.project = project
        report.save()
        
        messages.success(request, 'Report submitted successfully. Our team will review it.')
    else:
        messages.error(request, 'Please correct the errors in your report.')
    
    return redirect('projects:project_detail', slug=project.slug)

@login_required
@require_POST
def report_comment(request, comment_id):
    """Report inappropriate comment content"""
    comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
    
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.report_type = 'comment'
        report.comment = comment
        report.save()
        
        messages.success(request, 'Report submitted successfully. Our team will review it.')
    else:
        messages.error(request, 'Please correct the errors in your report.')
    
    return redirect('projects:project_detail', slug=comment.project.slug)

def category_detail(request, pk):
    """Display projects in a specific category"""
    category = get_object_or_404(Category, pk=pk, is_active=True)
    projects = Project.objects.filter(
        category=category,
        is_approved=True,
        status__in=['active', 'funded']
    ).select_related('creator').prefetch_related('tags', 'images')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'crowdfunding_projects/category_detail.html', context)

def tag_detail(request, pk):
    """Display projects with a specific tag"""
    tag = get_object_or_404(Tag, pk=pk)
    projects = Project.objects.filter(
        tags=tag,
        is_approved=True,
        status__in=['active', 'funded']
    ).select_related('creator', 'category').prefetch_related('tags', 'images')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    
    return render(request, 'crowdfunding_projects/tag_detail.html', context)

def user_projects(request, username):
    """Display projects created by a specific user"""
    user = get_object_or_404(User, username=username)
    projects = Project.objects.filter(
        creator=user,
        is_approved=True
    ).select_related('category').prefetch_related('tags', 'images')
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
    }
    
    return render(request, 'crowdfunding_projects/user_projects.html', context)
