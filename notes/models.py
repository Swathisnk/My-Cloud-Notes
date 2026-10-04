from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
import os

class Note(models.Model):
    SUBJECT_CHOICES = [
    ('Computer Science', 'Computer Science'),
    ('Mathematics', 'Mathematics'),
    ('Physics', 'Physics'),
    ('Chemistry', 'Chemistry'),

    # Engineering Subjects
    ('Engineering Graphics', 'Engineering Graphics'),
    ('Programming in C', 'Programming in C'),
    ('Python Programming', 'Python Programming'),
    ('Data Structures', 'Data Structures'),
    ('Object Oriented Programming', 'Object Oriented Programming'),
    ('Database Management Systems', 'Database Management Systems'),
    ('Operating Systems', 'Operating Systems'),
    ('Computer Networks', 'Computer Networks'),
    ('Software Engineering', 'Software Engineering'),
    ('Web Technologies', 'Web Technologies'),
    ('Design and Analysis of Algorithms', 'Design and Analysis of Algorithms'),
    ('Computer Organization', 'Computer Organization'),
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Machine Learning', 'Machine Learning'),
    ('Cloud Computing', 'Cloud Computing'),
    ('Cyber Security', 'Cyber Security'),
    ('Internet of Things', 'Internet of Things'),
    ('Engineering Economics', 'Engineering Economics'),
    ('Environmental Studies', 'Environmental Studies'),

    ('Business & Economics', 'Business & Economics'),
    ('Humanities & Social Sciences', 'Humanities & Social Sciences'),
    ('Other', 'Other'),
]

    title = models.CharField(max_length=150)
    description = models.TextField(max_length=500, blank=True)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, default='Other')
    file = models.FileField(upload_to='uploads/')
    file_size = models.FloatField(help_text="File size in MB")
    file_type = models.CharField(max_length=10, help_text="File extension (e.g., pdf, docx)")
    downloads = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def icon_class(self):
        """Returns the Bootstrap icon class depending on file type."""
        ext = self.file_type.lower()
        if 'pdf' in ext:
            return 'bi-file-earmark-pdf-fill text-danger'
        elif 'doc' in ext or 'docx' in ext:
            return 'bi-file-earmark-word-fill text-primary'
        return 'bi-file-earmark-text-fill text-secondary'

    @property
    def formatted_size(self):
        """Returns file size formatted as a reader friendly string."""
        if self.file_size < 1:
            return f"{int(self.file_size * 1024)} KB"
        return f"{self.file_size:.2f} MB"

    @property
    def average_rating(self):
        """Calculates the average rating of this note."""
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0.0

    @property
    def review_count(self):
        """Returns total reviews count."""
        return self.reviews.count()

    @property
    def star_range(self):
        """Returns lists for rendering empty/full star loops in templates."""
        avg = int(round(self.average_rating))
        return {
            'full': range(avg),
            'empty': range(5 - avg)
        }

class Review(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('note', 'user') # Users can leave only one review per note

    def __str__(self):
        return f"Review ({self.rating}/5) for {self.note.title} by {self.user.username}"
