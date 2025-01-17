from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#project serializers
from .models import Team, Project
from .models import Task,Note,Group,Objectives

User=get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # ...

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username','email','password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'owner', 'members', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

#This serializer will be used for Serializing "FOR GET QUERY" data only.
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description', 'owner', 'members', 'created_at']
        read_only_fields = ['owner', 'created_at']

#This serializer will be used for Serializing "FOR GET QUERY" data only.
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'team', 'tasks', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

   
    team = TeamSerializer()

    #the list of task and note IDs instead of nested serializers
    tasks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    notes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=['name','project']

class TaskSerializer(serializers.ModelSerializer):
    projects=ProjectSerializer(many=True,read_only=True)
    groups=GroupSerializer(many=True,read_only=True)
    #objectives=ObjectivesSerializer(many=True,source='objectivesserializers',read_only=True)
    class Meta:
        model=Task
        fields=['name','project','group','description']
        read_only_fields=['created_at']

class ObjectivesSerializer(serializers.ModelSerializer):
    tasks=TaskSerializer(many=True,read_only=True)
    class Meta:
        model=Objectives
        fields=['name','completed','task']
        read_only_fields=['created_at']

class NoteSerializer(serializers.ModelSerializer):
    projects=ProjectSerializer(many=True,read_only=True)
    group=GroupSerializer(many=True,read_only=True)
    class Meta:
        model=Note
        fields=['name','project','group','description']
        read_only_fields=['created_at']




        
