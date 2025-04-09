from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }
    
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    url = models.URLField()
    location = models.CharField(max_length=255)
    language = models.CharField(max_length=255)

    def save(self, *args, **kwargs):

        if self.user.projects.count()>=2 and not self.pk:
            raise ValidationError("you can create upto 2 projects")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class ProjectKeyword(models.Model):
    STATUS_CHOICES =[
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="keywords")
    keyword = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=255, default = "Unknown")

    class Meta:
        unique_together = ('project', 'keyword', 'location')
    def save(self, *args, **kwargs):
        
        if self.project.keywords.count() >= 10 and not self.pk:
            raise ValidationError("you can create upto 10 keywords per project")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.keyword} -{self.location}"