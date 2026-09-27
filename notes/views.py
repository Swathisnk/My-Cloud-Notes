from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import Q, Sum
from .models import Note, Review
import os

def index(request):
    """Catalog dashboard listing all notes with search and subject filter options."""
    search_query = request.GET.get('search', '')
    selected_subject = request.GET.get('subject', '')
    
    notes = Note.objects.all().order_by('-created_at')
    
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    if selected_subject:
        notes = notes.filter(subject=selected_subject)
        
    context = {
        'notes': notes,
        'search_query': search_query,
        'selected_subject': selected_subject,
    }
    return render(request, 'notes/index.html', context)

def register_view(request):
    """Handles student user registration with validation checks."""
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation checks
        if not username or not email or not password:
            messages.error(request, "All fields are required!")
            return render(request, 'notes/register.html')
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'notes/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return render(request, 'notes/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'notes/register.html')
            
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, f"Welcome to CloudNote, {username}! Your account has been created.")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Failed to register account: {str(e)}")
            return render(request, 'notes/register.html')
            
    return render(request, 'notes/register.html')

def login_view(request):
    """Authenticate and log in student users."""
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'notes/login.html')
            
    return render(request, 'notes/login.html')

def logout_view(request):
    """Securely log out the active user."""
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('login')

@login_required
def upload_note(request):
    """Enables users to publish note files with strict validation checks."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        subject = request.POST.get('subject', '').strip()
        
        if 'file' not in request.FILES:
            messages.error(request, "Please choose a note file to upload.")
            return render(request, 'notes/upload.html')
            
        uploaded_file = request.FILES['file']
        
        # Validations
        filename = uploaded_file.name
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if ext not in ['pdf', 'docx']:
            messages.error(request, "Invalid file format! Only PDF and DOCX files are allowed.")
            return render(request, 'notes/upload.html')
            
        # Check size (10 MB limit)
        max_size_bytes = 10 * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            messages.error(request, "File is too large! Maximum limit is 10MB.")
            return render(request, 'notes/upload.html')
            
        # Convert bytes to MB
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        try:
            # Create Note model record
            note = Note(
                title=title,
                description=description,
                subject=subject,
                file=uploaded_file,
                file_size=file_size_mb,
                file_type=ext,
                uploaded_by=request.user
            )
            note.save()
            messages.success(request, f"Congratulations! '{title}' has been successfully published.")
            return redirect('profile')
        except Exception as e:
            messages.error(request, f"Failed to upload note: {str(e)}")
            return render(request, 'notes/upload.html')
            
    return render(request, 'notes/upload.html')

def download_note(request, note_id):
    """Increments download tracking counter and serves the physical file secure payload."""
    note = get_object_or_404(Note, id=note_id)
    
    # Increment counter
    note.downloads += 1
    note.save()
    
    file_path = note.file.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
        # Preserve extension in response header attachment filename
        original_filename = os.path.basename(note.file.name)
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
        return response
    else:
        raise Http404("Document file does not exist on storage server.")

@login_required
def profile_view(request):
    """Serves details about user uploads and aggregates download traffic stats."""
    user_notes = Note.objects.filter(uploaded_by=request.user).order_by('-created_at')
    
    # Sum downloads
    total_downloads = user_notes.aggregate(total=Sum('downloads'))['total'] or 0
    
    context = {
        'notes': user_notes,
        'total_uploads': user_notes.count(),
        'total_downloads': total_downloads,
    }
    return render(request, 'notes/profile.html', context)

@login_required
def delete_note(request, note_id):
    """Allows user to remove their uploaded note files."""
    note = get_object_or_404(Note, id=note_id, uploaded_by=request.user)
    
    # Remove file from storage
    if note.file and os.path.exists(note.file.path):
        try:
            os.remove(note.file.path)
        except Exception:
            pass
            
    note.delete()
    messages.success(request, "Your note has been deleted.")
    return redirect('profile')

@user_passes_test(lambda u: u.is_staff, login_url='index')
def admin_dashboard(request):
    """Moderator control panel summarizing counts and enabling note deletions."""
    all_notes = Note.objects.all().order_by('-created_at')
    
    total_users = User.objects.count()
    total_notes = all_notes.count()
    total_downloads = all_notes.aggregate(total=Sum('downloads'))['total'] or 0
    
    context = {
        'notes': all_notes,
        'total_users': total_users,
        'total_notes': total_notes,
        'total_downloads': total_downloads,
    }
    return render(request, 'notes/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='index')
def admin_delete_note(request, note_id):
    """Enables staff/superusers to force delete any uploaded file."""
    note = get_object_or_404(Note, id=note_id)
    title = note.title
    
    # Remove file from disk
    if note.file and os.path.exists(note.file.path):
        try:
            os.remove(note.file.path)
        except Exception:
            pass
            
    note.delete()
    messages.success(request, f"Moderator Action: '{title}' has been force deleted.")
    return redirect('admin_dashboard')

def note_detail(request, note_id):
    """Details page showing note overview, file previews (PDF), and reviews feed."""
    note = get_object_or_404(Note, id=note_id)
    reviews = note.reviews.all().order_by('-created_at')
    
    # Check if this user has already left a review
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = note.reviews.filter(user=request.user).exists()
        
    context = {
        'note': note,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'notes/note_detail.html', context)

@login_required
def add_review(request, note_id):
    """Enables authenticated students to submit a document review/rating."""
    note = get_object_or_404(Note, id=note_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating:
            messages.error(request, "Please select a rating (1-5 stars).")
            return redirect('note_detail', note_id=note.id)
            
        try:
            # Check if user already reviewed
            review, created = Review.objects.get_or_create(
                note=note,
                user=request.user,
                defaults={'rating': int(rating), 'comment': comment}
            )
            
            if not created:
                messages.error(request, "You have already reviewed this note.")
            else:
                messages.success(request, "Thank you for your rating and review feedback!")
        except Exception as e:
            messages.error(request, f"Failed to submit review: {str(e)}")
            
    return redirect('note_detail', note_id=note.id)
