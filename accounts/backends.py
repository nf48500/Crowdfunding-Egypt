from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with their email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the username field contains an email
            if username and '@' in username:
                user = User.objects.get(email=username)
            else:
                # Fall back to username authentication
                user = User.objects.get(username=username)
            
            # Check if the password is correct
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
