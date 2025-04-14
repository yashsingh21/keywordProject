from rest_framework import generics,status,views,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer,ProjectSerializer, ProjectKeywordSerializer
from .models import Project, ProjectKeyword
from rest_framework.exceptions import ValidationError
# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        user=request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self,serializer):
        if self.request.user.projects.count()>= 2:
            raise ValidationError({"error": "You can create upto 2 projects"})
        serializer.save(user=self.request.user)

class ProjectKeywordCreateView(generics.CreateAPIView):
    queryset = ProjectKeyword.objects.all()
    serializer_class = ProjectKeywordSerializer
    permission_classes= (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        print("🚀 DEBUG: perform_create() called") 
        print("🚀 DEBUG: Received data:", self.request.data)

        project = serializer.validated_data['project']
        keywords_to_add = self.request.data.get('keywords', [])

        if project.user != self.request.user:
            raise ValidationError({"error": "You are not authorized to add keywords to this project"})
        
        existing_keyword_count = project.keywords.count()
        if existing_keyword_count + len(keywords_to_add) > 10:
            allowed_count= 10 - existing_keyword_count
            if allowed_count > 0:
                for keyword in keywords_to_add[:allowed_count]:
                    ProjectKeyword.objects.create(project=project,keyword=keyword, result={}, status = 'Pending')
                raise ValidationError({"error":f"only{allowed_count} keywords were added. Project limit is 10"})
            else:
                raise ValidationError({"error": "Project limit is 10 keywords only"})   
                
        serializer.save()