from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Comment, Rating, Donation, Report
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'details', 'category', 'tags', 'total_target',
            'start_date', 'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your project title'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your project in detail...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 5
            }),
            'total_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target amount in EGP',
                'min': '1000'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        total_target = cleaned_data.get('total_target')

        if start_date and end_date:
            if start_date <= timezone.now():
                raise ValidationError('Start date must be in the future.')
            
            if end_date <= start_date:
                raise ValidationError('End date must be after start date.')
            
            campaign_duration = end_date - start_date
            if campaign_duration < timedelta(days=1):
                raise ValidationError('Campaign must run for at least 1 day.')
            
            if campaign_duration > timedelta(days=365):
                raise ValidationError('Campaign cannot run for more than 1 year.')

        if total_target and total_target < 1000:
            raise ValidationError('Minimum target amount is 1,000 EGP.')

        return cleaned_data

class ProjectImageForm(forms.ModelForm):
    """Form for project images"""
    
    class Meta:
        model = Project
        fields = []  # This will be handled separately

class CommentForm(forms.ModelForm):
    """Form for project comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...',
                'maxlength': '1000'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 3:
            raise ValidationError('Comment must be at least 3 characters long.')
        return content.strip()

class ReplyForm(forms.ModelForm):
    """Form for comment replies"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write your reply...',
                'maxlength': '500'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 2:
            raise ValidationError('Reply must be at least 2 characters long.')
        return content.strip()

class RatingForm(forms.ModelForm):
    """Form for project ratings"""
    
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your review (optional)...',
                'maxlength': '500'
            })
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise ValidationError('Rating must be between 1 and 5.')
        return rating

class DonationForm(forms.ModelForm):
    """Form for project donations"""
    
    class Meta:
        model = Donation
        fields = ['amount', 'message', 'is_anonymous']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount in EGP',
                'min': '10',
                'step': '0.01'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Leave a message (optional)...',
                'maxlength': '200'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount < 10:
            raise ValidationError('Minimum donation amount is 10 EGP.')
        return amount

class ReportForm(forms.ModelForm):
    """Form for reporting inappropriate content"""
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please provide additional details about your report...',
                'maxlength': '500'
            })
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('Please provide more details about your report (at least 10 characters).')
        return description.strip()

class ProjectSearchForm(forms.Form):
    """Form for searching projects"""
    SEARCH_CHOICES = [
        ('title', 'Project Title'),
        ('tag', 'Project Tags'),
        ('category', 'Category'),
        ('creator', 'Creator'),
    ]
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects...'
        })
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='title',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    min_target = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min target amount'
        })
    )
    
    max_target = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max target amount'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Project.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the category queryset to only active categories
        from .models import Category
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        min_target = cleaned_data.get('min_target')
        max_target = cleaned_data.get('max_target')
        
        if min_target and max_target and min_target > max_target:
            raise ValidationError('Minimum target cannot be greater than maximum target.')
        
        return cleaned_data
