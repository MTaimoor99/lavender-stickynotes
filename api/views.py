import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse,Http404
from api.serializers import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.views.generic import TemplateView

#3rd party imports
from ipware import get_client_ip


#project imports
from api.version import version as api_version
from api.models import Team, Project
from api.serializers import TeamSerializer, ProjectSerializer
#from api.urls import urlpatterns

User=get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

#api docs
class DocsView(TemplateView):
    template_name = 'api/docs.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["api_version"] = api_version
        return context
    
#this will return all the routes available in the api
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/',
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/test/',
    ]
    # for urls in urlpatterns:
    #     routes.append(urls.pattern._route)

    return Response(routes)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            if 'text' not in data:
                return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
            text = data.get('text')
            data = f'Congratulation your API just responded to POST request with text: {text}'
            return Response({'response': data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
    return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)


class TeamCreateAndListAPIView(APIView):
    '''
    Get query can only be allowed to user with member or owner level permission.
    Psot can be done by anyone.
    '''
    def get(self,request,format=None):
        team_own=Team.objects.filter(owner=request.user)
        team_member=Team.objects.filter(members=request.user)

        serializer_own=TeamSerializer(team_own,many=True)
        serializer_member=TeamSerializer(team_member,many=True)

        return Response(
                        {'own':serializer_own.data,
                         'member':serializer_member.data,
                        })

    def post(self, request, format=None):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectCreateAndListAPIView(APIView):
    '''
    This class can be accessed with anyone with member level permission.

    '''
    def get (self,request,format=None):
        project_own=Project.objects.filter(team__owner=request.user)
        project_member=Project.objects.filter(team__members=request.user)

        serializer_own=ProjectSerializer(project_own,many=True)
        serializer_member=ProjectSerializer(project_member,many=True)

        return Response(
                        {'own_project':serializer_own.data,
                         'member_project':serializer_member.data,
                        })
    #Handle creation of project, Team is required
    #user need to pass the name of team in team field
    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    '''
    Every team has a unique slug, this slug is used to get the team detail.
    This whole class will need authentication+ access permission.
    Other user(member) can only access get method. all other function require
    owner permission.
    '''

    def get_object(self, slug):
        try:
            return Team.objects.get(slug=slug)
        except Team.DoesNotExist:
            raise Http404
    
    #this 'get' will return the team detail
    # It will also include members and  all project owned by this team.
    def get(self, request, slug, format=None):
        team = self.get_object(slug)
        serializer = TeamSerializer(team)
        return Response(serializer.data)

    def put(self, request, slug, format=None):
        team = self.get_object(slug=slug)
        serializer = TeamSerializer(team, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        team = self.get_object(slug=slug)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ProjectDetailView(APIView):
    '''
    All method except delete can be accessed by any member of team..
    '''
    
    def get_object(self, slug):
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise Http404
    #get  query need to return  notes and tasks of entire project
    def get(self, request, slug, format=None):
        project = self.get_object(slug)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, slug, format=None):
        project = self.get_object(slug=slug)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, format=None):
        project = self.get_object(slug=slug)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)