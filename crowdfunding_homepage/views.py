from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from crowdfunding_projects.models import Project, Category, Tag
from crowdfunding_projects.forms import ProjectSearchForm

def homepage(request):
    """Homepage with featured content and project listings"""
    
    # Get highest rated running projects for slider (top 5)
    top_rated_projects = Project.objects.filter(
        is_approved=True,
        status='active'
    ).annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    ).filter(
        avg_rating__isnull=False,
        rating_count__gte=1  # At least one rating
    ).order_by('-avg_rating', '-rating_count')[:5]
    
    # Get latest 5 projects
    latest_projects = Project.objects.filter(
        is_approved=True,
        status__in=['active', 'funded']
    ).select_related('category', 'creator').prefetch_related('tags', 'images').order_by('-created_at')[:5]
    
    # Get latest 5 featured projects
    featured_projects = Project.objects.filter(
        is_approved=True,
        is_featured=True,
        status__in=['active', 'funded']
    ).select_related('category', 'creator').prefetch_related('tags', 'images').order_by('-created_at')[:5]
    
    # Get all active categories with project counts
    categories = Category.objects.filter(is_active=True).annotate(
        project_count=Count('projects', filter=Q(projects__is_approved=True))
    ).order_by('name')
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        project_count=Count('projects', filter=Q(projects__is_approved=True))
    ).filter(project_count__gt=0).order_by('-project_count')[:10]
    
    # Search form
    search_form = ProjectSearchForm(request.GET)
    
    # Get trending projects (projects with most donations in last 7 days)
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    trending_projects = Project.objects.filter(
        is_approved=True,
        status='active',
        donations__created_at__gte=week_ago
    ).annotate(
        recent_donations=Count('donations', filter=Q(donations__created_at__gte=week_ago))
    ).filter(recent_donations__gt=0).order_by('-recent_donations', '-current_amount')[:3]
    
    # Get projects ending soon (within 7 days)
    ending_soon = Project.objects.filter(
        is_approved=True,
        status='active',
        end_date__lte=timezone.now() + timedelta(days=7),
        end_date__gt=timezone.now()
    ).select_related('category', 'creator').prefetch_related('tags', 'images').order_by('end_date')[:3]
    
    context = {
        'top_rated_projects': top_rated_projects,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'trending_projects': trending_projects,
        'ending_soon': ending_soon,
        'categories': categories,
        'popular_tags': popular_tags,
        'search_form': search_form,
    }
    
    return render(request, 'crowdfunding_homepage/homepage.html', context)

def search_results(request):
    """Advanced search results page"""
    search_form = ProjectSearchForm(request.GET)
    projects = None
    
    if search_form.is_valid():
        projects = Project.objects.filter(
            is_approved=True,
            status__in=['active', 'funded']
        ).select_related('category', 'creator').prefetch_related('tags', 'images')
        
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
        elif sort_by == 'funding':
            projects = projects.order_by('-current_amount')
        else:
            projects = projects.order_by('-created_at')
    
    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True).annotate(
        project_count=Count('projects', filter=Q(projects__is_approved=True))
    )
    
    context = {
        'search_form': search_form,
        'projects': projects,
        'categories': categories,
        'search_performed': bool(request.GET.get('search_query')),
    }
    
    return render(request, 'crowdfunding_homepage/search_results.html', context)

def category_explore(request):
    """Explore projects by category"""
    categories = Category.objects.filter(is_active=True).annotate(
        project_count=Count('projects', filter=Q(projects__is_approved=True))
    ).order_by('name')
    
    # Get featured projects from each category
    featured_by_category = {}
    for category in categories:
        featured_projects = Project.objects.filter(
            category=category,
            is_approved=True,
            is_featured=True,
            status__in=['active', 'funded']
        ).select_related('creator').prefetch_related('tags', 'images')[:3]
        featured_by_category[category] = featured_projects
    
    context = {
        'categories': categories,
        'featured_by_category': featured_by_category,
    }
    
    return render(request, 'crowdfunding_homepage/category_explore.html', context)

def about_page(request):
    """About page for the crowdfunding platform"""
    return render(request, 'crowdfunding_homepage/about.html')

def contact_page(request):
    """Contact page"""
    return render(request, 'crowdfunding_homepage/contact.html')

def terms_page(request):
    """Terms of service page"""
    return render(request, 'crowdfunding_homepage/terms.html')

def privacy_page(request):
    """Privacy policy page"""
    return render(request, 'crowdfunding_homepage/privacy.html')
