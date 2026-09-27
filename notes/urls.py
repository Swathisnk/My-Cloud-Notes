from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_note, name='upload'),
    path('download/<int:note_id>/', views.download_note, name='download'),
    path('profile/', views.profile_view, name='profile'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-delete/<int:note_id>/', views.admin_delete_note, name='admin_delete_note'),
    path('note/<int:note_id>/', views.note_detail, name='note_detail'),
    path('note/<int:note_id>/review/', views.add_review, name='add_review'),
]
