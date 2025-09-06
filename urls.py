from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project listing and search
    path('', views.project_list, name='project_list'),
    path('search/', views.project_list, name='project_search'),
    
    # Project detail and interaction
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    path('project/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('project/<slug:slug>/rate/', views.add_rating, name='add_rating'),
    path('project/<slug:slug>/donate/', views.add_donation, name='add_donation'),
    path('project/<slug:slug>/report/', views.report_content, name='report_project'),
    
    # Comment replies
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/report/', views.report_comment, name='report_comment'),
    
    # Project management (login required)
    path('create/', views.project_create, name='project_create'),
    path('project/<slug:slug>/edit/', views.project_edit, name='project_edit'),
    path('project/<slug:slug>/cancel/', views.project_cancel, name='project_cancel'),
    
    # Category and tag views
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('tag/<int:pk>/', views.tag_detail, name='tag_detail'),
    
    # User projects
    path('user/<str:username>/', views.user_projects, name='user_projects'),
]
