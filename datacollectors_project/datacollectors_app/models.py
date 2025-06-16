from django.db import models
# class Project(models.Model):
#     name = models.CharField(max_length=255, unique=True)
#     start_date = models.DateField(null=True, blank=True)
#     end_date = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return self.name


from django.db import models
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    scrum_master = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=150, null=True) # (Active, Finalised)
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
    

    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        
class TeamMember(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('deployed', 'Deployed'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('Foa', 'FOA'),
        ('Supervisor', 'Supervisor'),
        ('Backchecker', 'Backchecker'),
        ('Regular', 'Regular'),
        ('New Enumerator', 'New Enumerator'),
    ]

    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('data_collector', 'Data Collector'),
    ]
    ve_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    projects_count = models.PositiveIntegerField(default=0)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES)
    performance_score = models.PositiveIntegerField()
    rotation_rank = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    projects = models.ManyToManyField(Project, related_name='team_members', blank=True)

    def __str__(self):
        return f"{self.name} ({self.ve_code})"
    
    

class Ratings(models.Model):
    team_member = models.ForeignKey('TeamMember', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(null=True, blank=True)  # e.g., 1-5 stars
    feedback = models.TextField(blank=True, null=True)
    

    class Meta:
        unique_together = ('team_member', 'project')  # prevent duplicate assignment

    def __str__(self):
        return f"{self.team_member.name} - {self.project.name}"
