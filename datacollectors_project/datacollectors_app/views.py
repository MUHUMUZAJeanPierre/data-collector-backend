from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TeamMember
from .serializers import TeamMemberSerializer
from rest_framework.views import APIView
import random


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

    def list(self, request):
        queryset = self.get_queryset()

        status_param = request.query_params.get('status')
        unassigned = request.query_params.get('unassigned')

        if status_param:
            queryset = queryset.filter(status=status_param)

        if unassigned == 'true':
            queryset = queryset.filter(projects__isnull=True)

        queryset = queryset.prefetch_related('projects')
        
        serializer = self.get_serializer(queryset, many=True)
        
        data = []
        for item in serializer.data:
            member = queryset.get(id=item['id'])
            assigned_projects = [p.name for p in member.projects.all()]
            
            item['assigned_projects'] = assigned_projects
            item['current_project'] = assigned_projects[0] if assigned_projects else None
            item['assigned_projects_count'] = len(assigned_projects)
            data.append(item)
        
        return Response({
            "message": "Filtered team members retrieved successfully.",
            "data": data
        }, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Team member created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Team member creation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            # Add project information
            data = serializer.data
            assigned_projects = [p.name for p in instance.projects.all()]
            data['assigned_projects'] = assigned_projects
            data['current_project'] = assigned_projects[0] if assigned_projects else None
            data['assigned_projects_count'] = len(assigned_projects)
            
            return Response({
                "message": "Team member details retrieved.",
                "data": data
            }, status=status.HTTP_200_OK)
        except TeamMember.DoesNotExist:
            return Response({
                "message": "Team member not found."
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Add project information to response
            data = serializer.data
            assigned_projects = [p.name for p in instance.projects.all()]
            data['assigned_projects'] = assigned_projects
            data['current_project'] = assigned_projects[0] if assigned_projects else None
            data['assigned_projects_count'] = len(assigned_projects)
            
            return Response({
                "message": "Team member updated successfully.",
                "data": data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Team member update failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response({
            "message": "Team member deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)
    
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import TeamMember, Project

# class AssignProjectView(APIView):
#     def post(self, request):
#         data = request.data
#         project_name = data.get("projectName")
#         num_collectors = int(data.get("numCollectors", 0))

#         if not project_name or num_collectors <= 0:
#             return Response({"message": "Missing or invalid data."}, status=400)

#         # Get or create project
#         project, _ = Project.objects.get_or_create(name=project_name)

#         # First, try to get available team members
#         available_members = TeamMember.objects.filter(
#             status="available"
#         ).exclude(
#             projects=project  # Exclude members already assigned to this project
#         ).order_by('rotation_rank', '-performance_score')

#         selected_members = list(available_members[:num_collectors])

#         # If we don't have enough available members, check if all members are deployed
#         if len(selected_members) < num_collectors:
#             remaining_needed = num_collectors - len(selected_members)
            
#             # Check if all team members are deployed (no available members)
#             total_available = TeamMember.objects.filter(status="available").count()
            
#             if total_available == 0:
#                 # All members are deployed, select based on Performance Score and Rotation Rank only
#                 all_eligible_members = TeamMember.objects.exclude(
#                     projects=project  # Exclude members already on this specific project
#                 ).order_by('rotation_rank', '-performance_score')
                
#                 additional_members = list(all_eligible_members[:remaining_needed])
#                 selected_members.extend(additional_members)
#             else:
#                 # Some members are available but not enough, get from other statuses
#                 other_members = TeamMember.objects.exclude(
#                     status="available"
#                 ).exclude(
#                     id__in=[m.id for m in selected_members]
#                 ).exclude(
#                     projects=project
#                 ).order_by('rotation_rank', '-performance_score')
                
#                 additional_members = list(other_members[:remaining_needed])
#                 selected_members.extend(additional_members)

#         if len(selected_members) < num_collectors:
#             return Response({
#                 "message": f"Not enough eligible team members. Found {len(selected_members)} out of {num_collectors} needed."
#             }, status=400)

#         for member in selected_members:
#             member.projects.add(project)
#             member.projects_count += 1
#             member.status = "deployed"
#             member.save()

#         return Response({
#             "message": f"{len(selected_members)} members assigned to project {project_name}.",
#             "assigned": [
#                 {
#                     "name": m.name,
#                     "rotation_rank": m.rotation_rank,
#                     "performance_score": m.performance_score,
#                     "previous_status": m.status,
#                     "assignment_reason": "available" if m in available_members else ("all_deployed" if total_available == 0 else "other_status")
#                 }
#                 for m in selected_members
#             ]
#         }, status=200)

#     def get(self, request):
#         projects = Project.objects.all()
#         response_data = {}

#         for project in projects:
#             members = project.team_members.all()
#             response_data[project.name] = [
#                 {
#                     "name": m.name,
#                     "experience_level": m.experience_level,
#                     "performance_score": m.performance_score,
#                     "rotation_rank": m.rotation_rank,
#                     "role": m.role,
#                     "status": m.status,
#                 }
#                 for m in members
#             ]

#         return Response({"active_projects": response_data}, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import TeamMember, Project

class AssignProjectView(APIView):
    def post(self, request):
        data = request.data
        project_name = data.get("projectName")
        num_collectors = int(data.get("numCollectors", 0))
        num_supervisors = int(data.get("numSupervisors", 0))
        scrum_master = data.get("name")  # Scrum master name
        start_date = data.get("startDate")
        end_date = data.get("endDate")

        # Validation
        if not all([project_name, scrum_master, start_date, end_date]) or num_collectors <= 0:
            return Response({
                "message": "Missing or invalid data. Please provide project name, scrum master, dates, and valid number of collectors."
            }, status=400)

        # Parse dates and calculate duration
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            duration_days = (end_date_obj - start_date_obj).days
            
            if duration_days <= 0:
                return Response({
                    "message": "End date must be after start date."
                }, status=400)
                
        except ValueError:
            return Response({
                "message": "Invalid date format. Please use YYYY-MM-DD."
            }, status=400)

        # Get or create project with all details
        project, created = Project.objects.get_or_create(
            name=project_name,
            defaults={
                'scrum_master': scrum_master,
                'start_date': start_date_obj,
                'end_date': end_date_obj,
                'num_collectors_needed': num_collectors,
                'num_supervisors_needed': num_supervisors
            }
        )
        
        # If project already exists, update it with new details
        if not created:
            project.scrum_master = scrum_master
            project.start_date = start_date_obj
            project.end_date = end_date_obj
            project.num_collectors_needed = num_collectors
            project.num_supervisors_needed = num_supervisors
            project.save()

        # First, try to get available team members (data collectors)
        # Note: Adjust the role filtering based on your TeamMember model
        available_members_query = TeamMember.objects.filter(status="available").exclude(projects=project)
        
        # If you have a role field, uncomment the next line:
        # available_members_query = available_members_query.filter(role="data_collector")
        
        available_members = available_members_query.order_by('rotation_rank', '-performance_score')
        selected_members = list(available_members[:num_collectors])

        # If we don't have enough available members, check if all members are deployed
        if len(selected_members) < num_collectors:
            remaining_needed = num_collectors - len(selected_members)
            
            # Check if all team members are deployed (no available members)
            total_available_query = TeamMember.objects.filter(status="available")
            # If you have a role field, uncomment the next line:
            # total_available_query = total_available_query.filter(role="data_collector")
            total_available = total_available_query.count()
            
            if total_available == 0:
                # All members are deployed, select based on Performance Score and Rotation Rank only
                all_eligible_query = TeamMember.objects.exclude(projects=project)
                # If you have a role field, uncomment the next line:
                # all_eligible_query = all_eligible_query.filter(role="data_collector")
                
                all_eligible_members = all_eligible_query.order_by('rotation_rank', '-performance_score')
                additional_members = list(all_eligible_members[:remaining_needed])
                selected_members.extend(additional_members)
            else:
                # Some members are available but not enough, get from other statuses
                other_members_query = TeamMember.objects.exclude(status="available").exclude(
                    id__in=[m.id for m in selected_members]
                ).exclude(projects=project)
                # If you have a role field, uncomment the next line:
                # other_members_query = other_members_query.filter(role="data_collector")
                
                other_members = other_members_query.order_by('rotation_rank', '-performance_score')
                additional_members = list(other_members[:remaining_needed])
                selected_members.extend(additional_members)

        if len(selected_members) < num_collectors:
            return Response({
                "message": f"Not enough eligible data collectors. Found {len(selected_members)} out of {num_collectors} needed."
            }, status=400)

        # Assign data collectors to project
        for member in selected_members:
            member.projects.add(project)
            member.projects_count += 1
            member.status = "deployed"
            member.save()

        # Handle supervisors if needed (optional - depends on your TeamMember model)
        supervisor_members = []
        if num_supervisors > 0:
            available_supervisors_query = TeamMember.objects.filter(status="available").exclude(projects=project)
            # If you have a role field for supervisors, uncomment the next line:
            # available_supervisors_query = available_supervisors_query.filter(role="supervisor")
            
            available_supervisors = available_supervisors_query.order_by('rotation_rank', '-performance_score')
            supervisor_members = list(available_supervisors[:num_supervisors])
            
            for supervisor in supervisor_members:
                supervisor.projects.add(project)
                supervisor.projects_count += 1
                supervisor.status = "deployed"
                supervisor.save()

        return Response({
            "message": f"{len(selected_members)} data collectors and {len(supervisor_members)} supervisors assigned to project {project_name}.",
            "project_details": {
                "name": project_name,
                "scrum_master": scrum_master,
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": project.duration_days,
                "status": project.status,
                "num_collectors_needed": num_collectors,
                "num_supervisors_needed": num_supervisors
            },
            "assigned_collectors": [
                {
                    "name": m.name,
                    "rotation_rank": m.rotation_rank,
                    "performance_score": m.performance_score,
                    "previous_status": m.status,
                    "role": getattr(m, 'role', 'data_collector')
                }
                for m in selected_members
            ],
            "assigned_supervisors": [
                {
                    "name": s.name,
                    "rotation_rank": s.rotation_rank,
                    "performance_score": s.performance_score,
                    "role": getattr(s, 'role', 'supervisor')
                }
                for s in supervisor_members
            ]
        }, status=200)

    def get(self, request):
        projects = Project.objects.all()
        response_data = {}

        for project in projects:
            members = project.team_members.all()
            collectors = [m for m in members if getattr(m, 'role', None) == "data_collector"]
            supervisors = [m for m in members if getattr(m, 'role', None) == "supervisor"]
            
            response_data[project.name] = {
                "project_info": {
                    "name": project.name,
                    "scrum_master": project.scrum_master or 'Not specified',
                    "start_date": project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
                    "end_date": project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
                    "duration_days": project.duration_days,
                    "status": project.status,
                    "total_collectors": len(collectors),
                    "total_supervisors": len(supervisors),
                    "collectors_needed": project.num_collectors_needed,
                    "supervisors_needed": project.num_supervisors_needed
                },
                "data_collectors": [
                    {
                        "name": m.name,
                        "experience_level": getattr(m, 'experience_level', 'N/A'),
                        "performance_score": m.performance_score,
                        "rotation_rank": m.rotation_rank,
                        "role": getattr(m, 'role', 'data_collector'),
                        "status": m.status,
                    }
                    for m in collectors
                ],
                "supervisors": [
                    {
                        "name": m.name,
                        "experience_level": getattr(m, 'experience_level', 'N/A'),
                        "performance_score": m.performance_score,
                        "rotation_rank": m.rotation_rank,
                        "role": getattr(m, 'role', 'supervisor'),
                        "status": m.status,
                    }
                    for m in supervisors
                ]
            }

        return Response({"active_projects": response_data}, status=200)