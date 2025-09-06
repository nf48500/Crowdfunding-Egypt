from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    phone = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile Phone (e.g., 01012345678)'
        }),
        help_text="Enter a valid Egyptian mobile number (11 digits, starting with 01)"
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name', 
            'last_name', 
            'email', 
            'phone',
            'profile_picture',
            'password1', 
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field widgets
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('01'):
            raise forms.ValidationError('Phone number must start with 01.')
        if len(phone) != 11:
            raise forms.ValidationError('Phone number must be exactly 11 digits.')
        return phone

class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information (excluding email)"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'phone',
            'profile_picture',
            'birthdate',
            'facebook_profile',
            'country'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile Phone (e.g., 01012345678)'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'facebook_profile': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/yourprofile'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Country'
            })
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.startswith('01'):
            raise forms.ValidationError('Phone number must start with 01.')
        if phone and len(phone) != 11:
            raise forms.ValidationError('Phone number must be exactly 11 digits.')
        return phone

    def clean_facebook_profile(self):
        facebook_url = self.cleaned_data.get('facebook_profile')
        if facebook_url and 'facebook.com' not in facebook_url:
            raise forms.ValidationError('Please enter a valid Facebook profile URL.')
        return facebook_url
