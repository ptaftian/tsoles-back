import os
import io
import zipfile
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings  # Add this to manage file paths
from api.models import User, Bug, Log, AppVersion, Ticket, Examination
import logging
from api.serializer import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    BugSerializer,
    LogSerializer,
    AppVersionSerializer,
    TicketSerializer,
    ExaminationSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.db.models import Q

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/examinations/create/',
        '/api/examinations/',
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulations {request.user}, your API just responded to GET request."
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = request.data.get('text')  
        data = f'Congratulations, your API just responded to POST request with text: {text}.'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

class UserPagination(PageNumberPagination):
    page_size = 9  
    page_size_query_param = 'page_size'
    max_page_size = 100 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userListView(request):
    query = request.GET.get('search', None)
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |    
            Q(email__icontains=query) |       
            Q(serial_number__icontains=query) 
        )

    paginator = UserPagination()
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def updateUserView(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != user and not request.user.is_superuser:
        return Response({'error': 'You do not have permission to update this user.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def userDetailView(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != user and not request.user.is_superuser:
        return Response({'error': 'You do not have permission to access this user.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Bug Pagination Class
class BugPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBug(request):
    serializer = BugSerializer(data=request.data)

    if serializer.is_valid():
        bug = serializer.save(user=request.user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userBugs(request):
    bugs = Bug.objects.filter(user=request.user)  
    paginator = BugPagination()  
    paginated_bugs = paginator.paginate_queryset(bugs, request)  
    serializer = BugSerializer(paginated_bugs, many=True)
    return paginator.get_paginated_response(serializer.data)

class AllBugsPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size' 
    max_page_size = 100 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allBugsView(request):
    query = request.GET.get('search', None)
    bugs = Bug.objects.all()

    if query:
        bugs = bugs.filter(
            Q(hardwareCode__icontains=query) |  
            Q(softwareCode__icontains=query) |   
            Q(bugTxt__icontains=query)            
        )

    paginator = AllBugsPagination()
    paginated_bugs = paginator.paginate_queryset(bugs, request)
    serializer = BugSerializer(paginated_bugs, many=True)
    return paginator.get_paginated_response(serializer.data)

class LogPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createLog(request):
    serializer = LogSerializer(data=request.data)

    if serializer.is_valid():
        log = serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def allLogsView(request):
    query = request.GET.get('search', None)
    logs = Log.objects.all()  

    if query:
        logs = logs.filter(
            Q(hardwareCode__icontains=query) |  
            Q(softwareCode__icontains=query) |   
            Q(logTxt__icontains=query)            
        )

    paginator = LogPagination()  
    paginated_logs = paginator.paginate_queryset(logs, request)  
    serializer = LogSerializer(paginated_logs, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uploadVersion(request):
    serializer = AppVersionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getLatestVersion(request):
    try:
        latest_version = AppVersion.objects.latest('created_at')  
        serializer = AppVersionSerializer(latest_version)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AppVersion.DoesNotExist:
        return Response({'error': 'No versions available.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if request.user != user and not request.user.is_superuser:
            return Response({'error': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class TicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createTicket(request):
    serializer = TicketSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        ticket = serializer.save()  
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allTicketsView(request):
    query = request.GET.get('search', None)
    tickets = Ticket.objects.all() 

    if query:
        tickets = tickets.filter(
            Q(title__icontains=query) |         
            Q(body__icontains=query)            
        )

    paginator = TicketPagination()
    paginated_tickets = paginator.paginate_queryset(tickets, request)
    serializer = TicketSerializer(paginated_tickets, many=True)
    return paginator.get_paginated_response(serializer.data)

class ExaminationPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createExamination(request):

    logger.info(f"Request data: {request.data}")

    if 'download' not in request.FILES or not request.FILES['download'].name.endswith('.zip'):
        return Response({"error": "Only ZIP files are accepted for upload."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ExaminationSerializer(data=request.data)


    if serializer.is_valid():

        examination = serializer.save(customer=request.user)

        logger.info(f"Examination created successfully: {examination.design_title}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.error(f"Error creating examination: {serializer.errors}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listExaminations(request):
    examinations = Examination.objects.all()  
    paginator = ExaminationPagination()
    paginated_examinations = paginator.paginate_queryset(examinations, request)  
    serializer = ExaminationSerializer(paginated_examinations, many=True)
    return paginator.get_paginated_response(serializer.data)

class AppVersionPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def allVersionsView(request):
    versions = AppVersion.objects.all()  
    paginator = AppVersionPagination()   
    paginated_versions = paginator.paginate_queryset(versions, request)  
    serializer = AppVersionSerializer(paginated_versions, many=True)  
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBugById(request, bug_id):
    try:
        bug = Bug.objects.get(id=bug_id)  
        serializer = BugSerializer(bug)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Bug.DoesNotExist:
        return Response({'error': 'Bug not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getLogById(request, log_id):
    try:
        log = Log.objects.get(id=log_id) 
        serializer = LogSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Log.DoesNotExist:
        return Response({'error': 'Log not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTicketById(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id) 
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getExaminationById(request, examination_id):
    try:
        examination = Examination.objects.get(id=examination_id)  
        serializer = ExaminationSerializer(examination)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Examination.DoesNotExist:
        return Response({'error': 'Examination not found.'}, status=status.HTTP_404_NOT_FOUND)

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetchExaminationAndSTL(request, examination_id):
    try:
        # Get the Examination by ID
        examination = Examination.objects.get(id=examination_id)

        # Get the download URL for the file and construct full URL
        download_path = examination.download.url  # This is the relative URL
        full_download_url = f"{request.scheme}://{request.get_host()}{download_path}"

        # Log the full download URL for debugging
        logger.info(f"Attempting to download file from: {full_download_url}")

        # Fetch the ZIP file from the full URL
        response = requests.get(full_download_url)
        
        # Log the response status code for debugging
        logger.info(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            return Response({"error": "Failed to download the file.", "status_code": response.status_code}, status=response.status_code)

        # Extract the ZIP file in memory
        zip_content = response.content
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            # Search for the specific STL file
            stl_filename = 'Left_InternalStructure_Hollow.STL'
            
            if stl_filename in z.namelist():
                # Read the STL file content as binary
                stl_content = z.read(stl_filename)

                # Define the path where you want to save the STL file
                saved_stl_path = os.path.join(settings.MEDIA_ROOT, 'stl_files', stl_filename)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(saved_stl_path), exist_ok=True)

                # Save the STL content to a file
                with open(saved_stl_path, 'wb') as stl_file:
                    stl_file.write(stl_content)

                # Create the download URL
                download_url = f"{request.scheme}://{request.get_host()}/media/stl_files/{stl_filename}"
                
                # Return the download link to the client
                return Response({"message": "STL file saved successfully.", "download_link": download_url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "STL file not found in ZIP."}, status=status.HTTP_404_NOT_FOUND)

    except Examination.DoesNotExist:
        return Response({"error": "Examination not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)