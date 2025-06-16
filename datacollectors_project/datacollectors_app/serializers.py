from rest_framework import serializers
from .models import TeamMember,Project, Ratings

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields='__all__'
