from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date

# Egyptian phone number validator
egyptian_phone_validator = RegexValidator(
    regex=r"^01[0-2,5]\d{8}$",
    message="Enter a valid Egyptian mobile number (e.g., 01012345678)."
)

def validate_birthdate(value):
    """Validate that birthdate is not in the future and user is at least 13 years old"""
    if value > date.today():
        raise ValidationError('Birthdate cannot be in the future.')
    age = (date.today() - value).days // 365
    if age < 13:
        raise ValidationError('You must be at least 13 years old to register.')

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone = models.CharField(
        max_length=11, 
        validators=[egyptian_phone_validator],
        blank=False,
        help_text="Enter a valid Egyptian mobile number (e.g., 01012345678)"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pics/", 
        blank=True, 
        null=True
    )
    
    # Additional optional profile fields
    birthdate = models.DateField(
        null=True, 
        blank=True,
        validators=[validate_birthdate],
        help_text="Your date of birth (optional)"
    )
    facebook_profile = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Your Facebook profile URL (optional)"
    )
    country = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Your country (optional)"
    )
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_age(self):
        """Calculate user's age based on birthdate"""
        if self.birthdate:
            return (date.today() - self.birthdate).days // 365
        return None
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
