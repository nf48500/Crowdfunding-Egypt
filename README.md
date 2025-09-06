# Crowdfunding-Egypt
Crowdfunding Egypt - A Django platform that enables Egyptian creators to launch fundraising campaigns. Includes user registration with email verification, project creation with images, secure donations, and social features. Supports community-driven innovation across Egypt.
Crowdfunding Platform for Egypt 🇪🇬

A Django-based web platform designed to empower entrepreneurs and creators in Egypt to raise funds for their projects through community support.

🌟 Overview

This crowdfunding web application provides a complete solution for project creators to launch campaigns and receive donations from supporters. The platform includes user authentication, project management, donation processing, and social interaction features.

✨ Key Features

🔐 Authentication System

· User Registration with email, password, Egyptian phone validation, and profile picture
· Email Activation required before login (24-hour expiration)
· Secure Login with email and password
· Password Recovery system with email reset links
· User Profiles with editable information and activity tracking

🚀 Project Management

· Create Campaigns with titles, details, categories, and multiple images
· Set Funding Goals with specific targets in EGP
· Add Tags for better discoverability
· Time-bound Campaigns with start and end dates
· Project Ratings and user comments system

💰 Donation System

· Secure Donations to support projects
· Progress Tracking with percentage achieved indicators
· Donation History for users to track their contributions

🎯 Additional Features

· Project Categories managed by administrators
· Similar Projects recommendations based on tags
· Reporting System for inappropriate content
· Responsive Design for mobile and desktop devices

🛠️ Technology Stack

· Backend: Django 4.2.7
· Database: SQLite (Development), PostgreSQL (Production-ready)
· Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
· Authentication: Django Custom User Model
· File Handling: Pillow for image processing
· Email: Django SMTP backend with TLS support

📦 Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd crowdfunding
   ```
2. Set up virtual environment
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   # or
   env\Scripts\activate  # Windows
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create superuser
   ```bash
   python manage.py createsuperuser
   ```
6. Run development server
   ```bash
   python manage.py runserver
   ```

🚀 Usage

1. Registration: New users can sign up with their email, name, and Egyptian mobile number
2. Activation: Check your email to activate your account before logging in
3. Create Projects: Registered users can start fundraising campaigns
4. Discover Projects: Browse and support innovative ideas from Egyptian creators
5. Manage Profile: Update personal information and track your contributions

📁 Project Structure

```
crowdfunding/
├── accounts/          # User authentication and profiles
├── projects/         # Campaign and donation management
├── home/            # Main pages and static content
├── templates/       # HTML templates
├── static/          # CSS, JS, and static files
├── media/           # User-uploaded files
└── crowdfunding/    # Project configuration
```

🌍 Target Audience

· Egyptian entrepreneurs seeking funding
· Investors looking to support local projects
· Community members wanting to contribute to innovative ideas
· Administrators managing the platform and content

🔒 Security Features

· Email verification for new accounts
· Password hashing and secure authentication
· SQL injection prevention
· XSS protection
· CSRF tokens for form submissions
· Secure file upload handling

📈 Future Enhancements

· Integration with payment gateways for seamless transactions
· Social media sharing capabilities
· Advanced analytics for project creators
· Mobile application development
· Multi-language support
· API development for third-party integrations

🤝 Contributing

We welcome contributions from developers interested in improving crowdfunding opportunities in Egypt. Please feel free to submit issues, feature requests, or pull requests.

📄 License

This project is developed for educational and community purposes. Specific licensing details to be determined.
