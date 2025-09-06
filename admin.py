from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Tag, Project, ProjectImage, Comment, 
    Rating, Donation, Report
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'project_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']
    
    def project_count(self, obj):
        return obj.projects.count()
    project_count.short_description = 'Projects'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'project_count', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def project_count(self, obj):
        return obj.projects.count()
    project_count.short_description = 'Projects'

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'creator', 'category', 'status', 'progress_bar', 
        'total_target', 'current_amount', 'days_remaining', 
        'average_rating', 'is_featured', 'is_approved', 'created_at'
    ]
    list_filter = [
        'status', 'category', 'is_featured', 'is_approved', 
        'created_at', 'start_date', 'end_date'
    ]
    search_fields = ['title', 'details', 'creator__username', 'creator__email']
    list_editable = ['status', 'is_featured', 'is_approved']
    readonly_fields = [
        'current_amount', 'progress_percentage', 'days_remaining', 
        'average_rating', 'total_ratings', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'details', 'category', 'tags', 'creator')
        }),
        ('Financial', {
            'fields': ('total_target', 'current_amount', 'progress_percentage')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'days_remaining')
        }),
        ('Status & Approval', {
            'fields': ('status', 'is_featured', 'is_approved', 'approved_at', 'approved_by')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_ratings')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = 'success' if percentage >= 100 else 'warning' if percentage >= 50 else 'danger'
        return format_html(
            '<div class="progress" style="width: 100px; height: 20px;">'
            '<div class="progress-bar bg-{}" style="width: {}%">{}%</div>'
            '</div>',
            color, percentage, f"{percentage:.1f}"
        )
    progress_bar.short_description = 'Progress'
    
    def days_remaining(self, obj):
        days = obj.days_remaining
        if days == 0:
            return format_html('<span class="badge bg-danger">Ended</span>')
        elif days <= 7:
            return format_html('<span class="badge bg-warning">{} days</span>', days)
        else:
            return format_html('<span class="badge bg-success">{} days</span>', days)
    days_remaining.short_description = 'Days Left'
    
    def average_rating(self, obj):
        rating = obj.average_rating
        if rating == 0:
            return 'No ratings'
        stars = '★' * int(rating) + '☆' * (5 - int(rating))
        return format_html('{} ({:.1f}/5)', stars, rating)
    average_rating.short_description = 'Rating'

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'image_preview', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['project__title', 'caption']
    list_editable = ['order', 'is_primary']
    ordering = ['project', 'order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return 'No image'
    image_preview.short_description = 'Preview'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'user', 'content_preview', 'is_reply', 'parent', 
        'is_approved', 'reply_count', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'user__username', 'project__title']
    list_editable = ['is_approved']
    readonly_fields = ['reply_count', 'created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Reply'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'rating', 'review_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'project__title', 'review']
    readonly_fields = ['created_at', 'updated_at']
    
    def review_preview(self, obj):
        if obj.review:
            return obj.review[:100] + '...' if len(obj.review) > 100 else obj.review
        return 'No review'
    review_preview.short_description = 'Review'

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'user', 'amount', 'message_preview', 
        'is_anonymous', 'created_at'
    ]
    list_filter = ['is_anonymous', 'created_at']
    search_fields = ['user__username', 'project__title', 'message']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        if obj.message:
            return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
        return 'No message'
    message_preview.short_description = 'Message'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'reporter', 'report_type', 'project_or_comment', 'reason', 
        'is_resolved', 'resolved_by', 'created_at'
    ]
    list_filter = ['report_type', 'reason', 'is_resolved', 'created_at']
    search_fields = ['reporter__username', 'description']
    list_editable = ['is_resolved']
    readonly_fields = ['created_at']
    
    def project_or_comment(self, obj):
        if obj.report_type == 'project' and obj.project:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:crowdfunding_projects_project_change', args=[obj.project.pk]),
                obj.project.title
            )
        elif obj.report_type == 'comment' and obj.comment:
            return format_html(
                '<a href="{}">Comment on {}</a>',
                reverse('admin:crowdfunding_projects_comment_change', args=[obj.comment.pk]),
                obj.comment.project.title
            )
        return 'N/A'
    project_or_comment.short_description = 'Reported Item'
    
    def resolved_by(self, obj):
        if obj.resolved_by:
            return obj.resolved_by.username
        return '-'
    resolved_by.short_description = 'Resolved By'
