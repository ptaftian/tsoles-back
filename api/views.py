from django.shortcuts import render
from django.http import JsonResponse
from api.models import User, Bug, Log, AppVersion  # Ensure all models are imported
from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer, BugSerializer, LogSerializer, AppVersionSerializer  # Import all required serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework import status

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
        '/api/token/refresh/'
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulations {request.user}, your API just responded to GET request."
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = request.POST.get('text')
        data = f'Congratulations, your API just responded to POST request with text: {text}.'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

# User Pagination Class
class UserPagination(PageNumberPagination):
    page_size = 9  
    page_size_query_param = 'page_size'
    max_page_size = 100 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userListView(request):
    users = User.objects.all()
    paginator = UserPagination()  
    paginated_users = paginator.paginate_queryset(users, request)  
    serializer = UserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)

# User update view (PATCH)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def updateUserView(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the requesting user has permission to update this user
    if request.user != user and not request.user.is_superuser:
        return Response({'error': 'You do not have permission to update this user.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user, data=request.data, partial=True)  # partial=True allows partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        bug = serializer.save(user=request.user)  # Set the user to the currently authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userBugs(request):
    bugs = request.user.bugs.all()  # Fetch all bugs for the authenticated user
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
    bugs = Bug.objects.all()  # Get all bugs
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
        log = serializer.save(user=request.user)  # Attach the user to the log
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def allLogsView(request):
    logs = Log.objects.all()  # Get all logs
    paginator = LogPagination()  

    paginated_logs = paginator.paginate_queryset(logs, request)  
    serializer = LogSerializer(paginated_logs, many=True)

    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uploadVersion(request):
    serializer = AppVersionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save the version details
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getLatestVersion(request):
    try:
        latest_version = AppVersion.objects.latest('created_at')  # Get the latest version
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