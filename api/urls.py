from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    path('users/', views.userListView, name='user_list'),
    path('users/<int:user_id>/', views.deleteUser, name='delete_user'),  # For deleting users
    path('users/<int:user_id>/update/', views.updateUserView, name='user_update'),  # Updated path for user update
    path('logs/', views.createLog, name='create_log'),
    path('logs/all/', views.allLogsView, name='all_logs'),
    path('bugs/', views.createBug, name='create_bug'),
    path('bugs/my/', views.userBugs, name='user_bugs'),
    path('bugs/all/', views.allBugsView, name='all_bugs'),
    path('upload-version/', views.uploadVersion, name='upload_version'),
    path('latest-version/', views.getLatestVersion, name='latest_version'),
    path('', views.getRoutes),
]