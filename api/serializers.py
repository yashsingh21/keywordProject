from rest_framework import serializers
from .models import User,Project, ProjectKeyword
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6,write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()
    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
    class Meta:
        model = User
        fields = ['password','username','tokens']
    def validate(self, attrs):
        username = attrs.get('username','')
        password = attrs.get('password','')
        user = auth.authenticate(username=username,password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'user', 'name', 'url', 'location', 'language']
        extra_kwargs = {'user': {'read_only': True}}

class ProjectKeywordSerializer(serializers.ModelSerializer):
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=255), write_only=True
    )
    location = serializers.CharField(max_length=255)
    class Meta:
        model = ProjectKeyword
        fields = ['id', 'project', 'keywords','location',  'status']
    def validate(self, data):
        """
        Validate that the user is not adding duplicate keywords for the same project & location.
        """
        project = data.get("project")
        keywords_list = data.get("keywords", [])
        location = data.get("location")

        # ✅ Prevent duplicate keyword for the same project + location
        existing_keywords = ProjectKeyword.objects.filter(
            project=project, location=location
        ).values_list('keyword', flat=True)

        duplicates = set(keywords_list) & set(existing_keywords)
        if duplicates:
            raise serializers.ValidationError(
                {"error": f"These keywords already exist for this project & location: {', '.join(duplicates)}"}
            )

        return data
    def create(self, validated_data):
        project = validated_data['project']
        location = validated_data['location']
        keywords_list = validated_data.pop('keywords', []) 
         # Get list of keywords
        print("DEBUG: Project ID:", project.id)  # ✅ Check project ID
        print("DEBUG: Keywords received:", keywords_list)

        existing_count = ProjectKeyword.objects.filter(project=project).count()
        if existing_count + len(keywords_list) > 10:
            raise serializers.ValidationError({"error": "A project can have a maximum of 10 keywords."})

        keyword_instances = [
            ProjectKeyword(project=project, keyword=kw, location=location) for kw in keywords_list
        ]
        created_keywords = ProjectKeyword.objects.bulk_create(keyword_instances)
        print("DEBUG: Keywords inserted:", created_keywords)
        return created_keywords[0]
    
    def to_representation(self, instance):
        """Customize response to return all created keywords."""
        if isinstance(instance, list):
            return [super().to_representation(obj) for obj in instance]
        return super().to_representation(instance)