# Crowdfunding Platform

A modern Django-based crowdfunding platform with a complete authentication system.

## Features

### 1. Authentication System

#### Registration
- **Required Fields:**
  - First name
  - Last name
  - Email
  - Username
  - Password
  - Confirm password
  - Mobile phone (validated against Egyptian phone numbers)
  - Profile picture (optional)

#### Registration
- Users are automatically activated upon registration
- No email activation required
- Immediate access to the platform

#### Login
- Email-based authentication
- Password validation
- Facebook login placeholder (bonus feature)

#### Forgot Password (Bonus)
- Users can request password reset via email
- Secure password reset links with 24-hour expiration
- Professional email templates for password reset
- Complete password reset workflow

#### User Profile
- **Profile Viewing**: Users can view their complete profile information
- **Project Management**: View all created projects in one place
- **Donation History**: Track all donations made to projects
- **Profile Editing**: Edit all profile data except email address
- **Additional Information**: Optional fields for birthdate, Facebook profile, and country
- **Account Deletion**: Secure account deletion with confirmation modal
- **Profile Picture**: Upload and manage profile pictures

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crowdfunding
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Registration: http://127.0.0.1:8000/accounts/register/
   - Login: http://127.0.0.1:8000/accounts/login/
   - Password Reset: http://127.0.0.1:8000/accounts/password-reset/
   - User Profile: http://127.0.0.1:8000/accounts/profile/

## Configuration

### Email Settings

For development, emails are printed to the console. For production, update the email settings in `crowdfunding/settings.py`:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"
EMAIL_USE_TLS = True
```

### Media Files

Profile pictures are stored in the `media/profile_pics/` directory. Make sure the directory is writable.

## Project Structure

```
crowdfunding/
├── accounts/                 # Authentication app
│   ├── models.py            # CustomUser model
│   ├── forms.py             # Registration and profile forms
│   ├── views.py             # Authentication and profile views
│   ├── urls.py              # Authentication URLs
│   ├── backends.py          # Custom authentication backend
│   └── templates/           # Authentication templates
├── crowdfunding/            # Project settings
│   ├── settings.py          # Django settings
│   └── urls.py              # Main URL configuration
├── home/                    # Home app
├── projects/                # Projects app
├── manage.py                # Django management script
└── requirements.txt          # Python dependencies
```

## Custom User Model

The platform uses a custom user model (`CustomUser`) that extends Django's `AbstractUser` with:

- Email as the primary identifier
- Egyptian phone number validation
- Profile picture support
- Additional profile fields (birthdate, Facebook, country)
- Custom authentication backend for email-based login

## Phone Number Validation

Egyptian mobile numbers are validated using regex pattern: `^01[0-2,5]\d{8}$`

Valid formats:
- 01012345678
- 01112345678
- 01212345678
- 01512345678

## Security Features

- CSRF protection
- Password validation
- Account activation requirement
- Secure token generation
- Input sanitization
- Password reset functionality
- Profile data validation

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 guidelines and Django best practices.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
