from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('on-hold', 'On Hold'),
        ('planning', 'Planning'),
        ('finalised', 'Finalised'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    scrum_master = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='planning',
        null=True, 
        blank=True
    )
    num_collectors_needed = models.PositiveIntegerField(default=0)
    num_supervisors_needed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    @property
    def collectors_needed(self):
        """Alias for compatibility with frontend"""
        return self.num_collectors_needed
    
    @property
    def supervisors_needed(self):
        """Alias for compatibility with frontend"""
        return self.num_supervisors_needed
    
    @property
    def total_members_needed(self):
        return self.num_collectors_needed + self.num_supervisors_needed
    
    @property
    def assigned_members_count(self):
        return self.team_members.count()
    
    @property
    def is_fully_staffed(self):
        return self.assigned_members_count >= self.total_members_needed

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class TeamMember(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('deployed', 'Deployed'),
        ('inactive', 'Inactive'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('foa', 'FOA'),
        ('supervisor', 'Supervisor'),
        ('backchecker', 'Backchecker'),
        ('regular', 'Regular'),
        ('new_enumerator', 'New Enumerator'),
    ]

    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('data_collector', 'Data Collector'),
    ]
    
    # Core fields
    ve_code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    
    # Experience and performance
    projects_count = models.PositiveIntegerField(default=0)
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVEL_CHOICES,
        default='regular'
    )
    performance_score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    rotation_rank = models.PositiveIntegerField(default=1)
    
    # Status and relationships
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        db_index=True
    )
    projects = models.ManyToManyField(
        Project, 
        related_name='team_members', 
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ve_code})"
    
    @property
    def assigned_projects(self):
        """Get list of project names this member is assigned to"""
        return list(self.projects.values_list('name', flat=True))
    
    @property
    def current_project_count(self):
        """Count of currently assigned projects"""
        return self.projects.filter(status='active').count()
    
    @property
    def average_rating(self):
        """Calculate average rating across all projects"""
        ratings = self.ratings_set.filter(rating__isnull=False)
        if ratings.exists():
            return round(ratings.aggregate(avg=models.Avg('rating'))['avg'], 2)
        return None

    class Meta:
        ordering = ['name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"


class Ratings(models.Model):
    """Rating model for team member performance on projects"""
    team_member = models.ForeignKey(
        TeamMember, 
        on_delete=models.CASCADE,
        db_index=True
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE,
        db_index=True
    )
    rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Meta fields for tracking
    rated_by = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Who provided this rating"
    )
    
    class Meta:
        unique_together = ('team_member', 'project')
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['team_member', 'project']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        rating_display = f"{self.rating}/5" if self.rating else "No rating"
        return f"{self.team_member.name} - {self.project.name} ({rating_display})"
    
    def clean(self):
        """Validate that rating is within acceptable range"""
        from django.core.exceptions import ValidationError
        if self.rating is not None and (self.rating < 1 or self.rating > 5):
            raise ValidationError("Rating must be between 1 and 5")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)