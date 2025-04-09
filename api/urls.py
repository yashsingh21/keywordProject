from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginAPIView.as_view(),name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('projects/', views.ProjectCreateView.as_view(), name='create_project'),
    path('keywords/', views.ProjectKeywordCreateView.as_view(), name='add_keywords'),
]
