from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # JWT Authentication
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Registration and Detail Management
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('users/', views.userListView, name='user_list'),
    path('users/<int:user_id>/', views.userDetailView, name='user_detail'),
    path('users/<int:user_id>/delete/', views.deleteUser, name='delete_user'),
    path('users/<int:user_id>/update/', views.updateUserView, name='user_update'),

    # Log Management
    path('logs/', views.createLog, name='create_log'),
    path('logs/all/', views.allLogsView, name='all_logs'),
    path('logs/<int:log_id>/', views.getLogById, name='get_log_by_id'),
    
    # Bug Management
    path('bugs/', views.createBug, name='create_bug'),
    path('bugs/my/', views.userBugs, name='user_bugs'),
    path('bugs/all/', views.allBugsView, name='all_bugs'),
    path('bugs/<int:bug_id>/', views.getBugById, name='get_bug_by_id'),

    # App Versioning
    path('upload-version/', views.uploadVersion, name='upload_version'),
    path('latest-version/', views.getLatestVersion, name='latest_version'),

    # Examination Management
    path('examinations/', views.listExaminations, name='list_examinations'),
    path('examinations/create/', views.createExamination, name='create_examination'),  # Ensure file upload is handled here
    path('examinations/<int:examination_id>/', views.getExaminationById, name='get_examination_by_id'),
    path('examinations/<int:examination_id>/fetch-stl/', views.fetchExaminationAndSTL, name='fetch_examination_and_stl'),

    # Ticket Management
    path('tickets/', views.allTicketsView, name='all_tickets'),
    path('tickets/create/', views.createTicket, name='create_ticket'),
    path('tickets/<int:ticket_id>/', views.getTicketById, name='get_ticket_by_id'),

    # General API Health Check or Route List
    path('test/', views.testEndPoint, name='test'),
    path('', views.getRoutes, name='api_routes'),

    # Versions and other utility endpoints
    path('versions/all/', views.allVersionsView, name='all_versions'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)