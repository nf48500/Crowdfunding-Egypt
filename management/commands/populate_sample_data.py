from django.core.management.base import BaseCommand
from crowdfunding_projects.models import Category, Tag
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample categories and tags'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample categories...')
        
        # Create sample categories
        categories_data = [
            {
                'name': 'Technology',
                'description': 'Innovative tech projects and startups',
                'icon': 'laptop-code',
                'color': '#667eea'
            },
            {
                'name': 'Art & Design',
                'description': 'Creative art projects and design initiatives',
                'icon': 'palette',
                'color': '#e91e63'
            },
            {
                'name': 'Music',
                'description': 'Musical projects and albums',
                'icon': 'music',
                'color': '#9c27b0'
            },
            {
                'name': 'Film & Video',
                'description': 'Film projects and video content',
                'icon': 'video',
                'color': '#ff5722'
            },
            {
                'name': 'Games',
                'description': 'Video games and interactive entertainment',
                'icon': 'gamepad',
                'color': '#4caf50'
            },
            {
                'name': 'Publishing',
                'description': 'Books, magazines, and digital content',
                'icon': 'book',
                'color': '#795548'
            },
            {
                'name': 'Food & Craft',
                'description': 'Culinary projects and handmade crafts',
                'icon': 'utensils',
                'color': '#ff9800'
            },
            {
                'name': 'Fashion & Wearables',
                'description': 'Fashion design and wearable technology',
                'icon': 'tshirt',
                'color': '#f44336'
            },
            {
                'name': 'Health & Fitness',
                'description': 'Health products and fitness innovations',
                'icon': 'heartbeat',
                'color': '#00bcd4'
            },
            {
                'name': 'Education',
                'description': 'Educational tools and learning platforms',
                'icon': 'graduation-cap',
                'color': '#3f51b5'
            }
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        self.stdout.write('Creating sample tags...')
        
        # Create sample tags
        tags_data = [
            'Innovation', 'Startup', 'Mobile App', 'Web App', 'AI', 'Machine Learning',
            'Blockchain', 'IoT', 'VR', 'AR', 'Gaming', 'Indie Game', 'Mobile Game',
            'PC Game', 'Console Game', 'Art', 'Digital Art', 'Painting', 'Sculpture',
            'Photography', 'Music', 'Album', 'EP', 'Single', 'Concert', 'Film',
            'Documentary', 'Short Film', 'Feature Film', 'Animation', 'Comic',
            'Graphic Novel', 'Book', 'Magazine', 'Podcast', 'Food', 'Restaurant',
            'Cookbook', 'Craft', 'Handmade', 'DIY', 'Fashion', 'Clothing',
            'Accessories', 'Jewelry', 'Health', 'Fitness', 'Wellness', 'Medical',
            'Education', 'Online Course', 'Tutorial', 'Workshop', 'Community',
            'Social Impact', 'Environment', 'Sustainability', 'Charity', 'Non-profit'
        ]
        
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'color': '#6c757d'}
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
            else:
                self.stdout.write(f'Tag already exists: {tag.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
