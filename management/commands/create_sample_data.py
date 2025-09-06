from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crowdfunding_projects.models import Category, Tag, Project
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing the crowdfunding platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Technology', 'icon': 'laptop', 'color': '#667eea'},
            {'name': 'Art & Design', 'icon': 'palette', 'color': '#764ba2'},
            {'name': 'Music', 'icon': 'music', 'color': '#f093fb'},
            {'name': 'Film & Video', 'icon': 'video', 'color': '#4facfe'},
            {'name': 'Games', 'icon': 'gamepad', 'color': '#43e97b'},
            {'name': 'Publishing', 'icon': 'book', 'color': '#fa709a'},
            {'name': 'Food & Craft', 'icon': 'utensils', 'color': '#ffecd2'},
            {'name': 'Fashion', 'icon': 'tshirt', 'color': '#fcb69f'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'description': f'Amazing {cat_data["name"].lower()} projects'
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create tags
        tags_data = [
            'Innovation', 'Creative', 'Sustainable', 'Community', 'Education',
            'Health', 'Environment', 'Social Impact', 'Startup', 'Mobile App',
            'Web App', 'Hardware', 'Software', 'Design', 'Photography',
            'Illustration', 'Animation', 'Documentary', 'Short Film', 'Album',
            'EP', 'Concert', 'Board Game', 'Video Game', 'Mobile Game',
            'Cookbook', 'Restaurant', 'Fashion Line', 'Accessories', 'Jewelry'
        ]
        
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        # Create sample projects if no projects exist
        if Project.objects.count() == 0:
            self.create_sample_projects()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_sample_projects(self):
        """Create sample projects for testing"""
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        sample_projects = [
            {
                'title': 'Smart Home Automation System',
                'details': 'A revolutionary IoT system that makes your home smarter and more energy-efficient.',
                'category': categories[0] if categories else None,
                'total_target': 50000,
                'current_amount': 35000,
                'is_featured': True,
                'tags': ['Innovation', 'Hardware', 'Technology']
            },
            {
                'title': 'Eco-Friendly Fashion Collection',
                'details': 'Sustainable fashion line made from recycled materials.',
                'category': categories[7] if len(categories) > 7 else categories[0],
                'total_target': 25000,
                'current_amount': 18000,
                'is_featured': True,
                'tags': ['Fashion', 'Sustainable', 'Environment']
            },
            {
                'title': 'Educational Mobile App for Kids',
                'details': 'Interactive learning app that makes education fun for children.',
                'category': categories[0] if categories else None,
                'total_target': 30000,
                'current_amount': 22000,
                'is_featured': False,
                'tags': ['Education', 'Mobile App', 'Technology']
            },
            {
                'title': 'Community Garden Project',
                'details': 'Creating a community garden to promote sustainable living.',
                'category': categories[6] if len(categories) > 6 else categories[0],
                'total_target': 15000,
                'current_amount': 12000,
                'is_featured': False,
                'tags': ['Community', 'Environment', 'Sustainable']
            },
            {
                'title': 'Indie Music Album',
                'details': 'Recording and producing a full-length indie rock album.',
                'category': categories[2] if len(categories) > 2 else categories[0],
                'total_target': 20000,
                'current_amount': 15000,
                'is_featured': True,
                'tags': ['Music', 'Album', 'Creative']
            }
        ]
        
        for i, project_data in enumerate(sample_projects):
            # Set dates
            start_date = timezone.now() - timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            project = Project.objects.create(
                title=project_data['title'],
                details=project_data['details'],
                category=project_data['category'],
                creator=user,
                total_target=project_data['total_target'],
                current_amount=project_data['current_amount'],
                start_date=start_date,
                end_date=end_date,
                is_featured=project_data['is_featured'],
                is_approved=True,
                status='active'
            )
            
            # Add tags
            for tag_name in project_data['tags']:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    project.tags.add(tag)
                except Tag.DoesNotExist:
                    pass
            
            self.stdout.write(f'Created project: {project.title}')
