from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.db.models import Avg, Count
import uuid

User = get_user_model()

class Category(models.Model):
    """Project categories managed by admins"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default="#667eea", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:category_detail', kwargs={'pk': self.pk})

class Tag(models.Model):
    """Project tags for categorization and search"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#6c757d", help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:tag_detail', kwargs={'pk': self.pk})

class Project(models.Model):
    """Crowdfunding project model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('funded', 'Fully Funded'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='projects')
    tags = models.ManyToManyField(Tag, related_name='projects', blank=True)
    
    # Creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    
    # Financial
    total_target = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(1000)],  # Minimum 1000 EGP
        help_text="Target amount in EGP"
    )
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timeline
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Status and Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_projects'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{uuid.uuid4().hex[:8]}-{self.title.lower().replace(' ', '-')}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'slug': self.slug})

    @property
    def progress_percentage(self):
        """Calculate funding progress percentage"""
        if self.total_target and self.total_target > 0:
            return min((self.current_amount / self.total_target) * 100, 100)
        return 0

    @property
    def days_remaining(self):
        """Calculate days remaining in campaign"""
        if self.status == 'active':
            remaining = self.end_date - timezone.now()
            return max(remaining.days, 0)
        return 0

    @property
    def is_cancellable(self):
        """Check if project can be cancelled (less than 25% funded)"""
        return self.status == 'active' and self.progress_percentage < 25

    @property
    def average_rating(self):
        """Calculate average project rating"""
        return self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    @property
    def total_ratings(self):
        """Get total number of ratings"""
        return self.ratings.count()
    
    @property
    def status_color(self):
        """Get Bootstrap color class for status"""
        status_colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'active': 'success',
            'funded': 'info',
            'cancelled': 'danger',
            'completed': 'primary',
        }
        return status_colors.get(self.status, 'secondary')

    def get_similar_projects(self, limit=4):
        """Get similar projects based on tags and category"""
        similar = Project.objects.filter(
            models.Q(category=self.category) | models.Q(tags__in=self.tags.all()),
            status='active',
            is_approved=True
        ).exclude(pk=self.pk).distinct()
        
        # Score based on tag matches
        scored_projects = []
        for project in similar:
            score = 0
            if project.category == self.category:
                score += 2
            common_tags = set(project.tags.all()) & set(self.tags.all())
            score += len(common_tags)
            scored_projects.append((project, score))
        
        # Sort by score and return top results
        scored_projects.sort(key=lambda x: x[1], reverse=True)
        return [project for project, score in scored_projects[:limit]]

class ProjectImage(models.Model):
    """Multiple images for a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per project
            ProjectImage.objects.filter(project=self.project, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class Comment(models.Model):
    """Project comments with reply support"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def reply_count(self):
        return self.replies.filter(is_approved=True).count()

class Rating(models.Model):
    """Project ratings by users"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}/5 by {self.user.username} on {self.project.title}"

class Donation(models.Model):
    """Project donations by users"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_donations')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(10)],  # Minimum 10 EGP
        help_text="Donation amount in EGP"
    )
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.amount} EGP by {self.user.username} to {self.project.title}"

    def save(self, *args, **kwargs):
        # Update project current amount
        if not self.pk:  # New donation
            self.project.current_amount += self.amount
            self.project.save()
        super().save(*args, **kwargs)

class Report(models.Model):
    """Reports for inappropriate projects or comments"""
    REPORT_TYPES = [
        ('project', 'Project'),
        ('comment', 'Comment'),
    ]
    
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake or Misleading'),
        ('violence', 'Violence or Hate Speech'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter.username} on {self.get_report_type_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.report_type == 'project' and not self.project:
            raise ValidationError('Project must be specified for project reports')
        if self.report_type == 'comment' and not self.comment:
            raise ValidationError('Comment must be specified for comment reports')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
