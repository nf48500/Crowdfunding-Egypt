from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    # Main homepage
    path('', views.homepage, name='homepage'),
    
    # Search and exploration
    path('search/', views.search_results, name='search_results'),
    path('explore/', views.category_explore, name='category_explore'),
    
    # Static pages
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('terms/', views.terms_page, name='terms'),
    path('privacy/', views.privacy_page, name='privacy'),
]
