# from django.contrib import admin
# from .models import TeamMember

# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ('ve_code', 'name', 'role', 'projects_count', 'experience_level', 'performance_score', 'rotation_rank', 'status', 'current_project')


from django.contrib import admin
from .models import TeamMember

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        've_code', 'name', 'role', 'projects_count',
        'experience_level', 'performance_score',
    )