# members/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamMemberViewSet, AssignProjectView

router = DefaultRouter()
router.register(r'teammembers', TeamMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('assign-project/', AssignProjectView.as_view(), name='assign_project')
]
