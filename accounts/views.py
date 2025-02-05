from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from .serializer import (
    EmployeeProfileSerializer,
    EmployerProfileSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
    UserSerializer,
    ServiceSerializer
)
from .models import User, EmployeeProfile, EmployerProfile, Service
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
import re

class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer


    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_type": user.user_type})


obtain_auth_token = ObtainAuthToken.as_view()

@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    # Optionally delete the user's token
    try:
        request.user.auth_token.delete()  # Delete the token for token-based auth
    except (AttributeError, Token.DoesNotExist):
        pass
    logout(request)  # Log out from the session
    return Response({'message': 'Logged out successfully'})

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    serializer = UpdateUserSerializer(instance=user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_employee(request):
    try:
        employee_profile = request.user.employee_profile
    except EmployeeProfile.DoesNotExist:
        return Response({"detail": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get user data
    user_data = request.data.get("user", {})

    # Ensure user_data is a dictionary
    if isinstance(user_data, dict):
        for field, value in user_data.items():
            if hasattr(request.user, field):
                setattr(request.user, field, value)
        request.user.save()
    else:
        return Response({"detail": "Invalid user data format. Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the employee profile
    serializer = EmployeeProfileSerializer(instance=employee_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # Serialize the user data
        user_serializer = UserSerializer(request.user)

        # Prepare the response data including user and employee profile
        response_data = {
            "user": user_serializer.data,
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_employer(request):
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        return Response({"detail": "Employer profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get user data
    user_data = request.data.get("user", {})
    employer_profile_data = request.data.get("employer_profile", {})

    # Ensure user_data is a dictionary
    if isinstance(user_data, dict):
        for field, value in user_data.items():
            if hasattr(request.user, field):
                setattr(request.user, field, value)
        request.user.save()
    else:
        return Response({"detail": "Invalid user data format. Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure employer_profile_data is a dictionary
    if isinstance(employer_profile_data, dict):
        # Update the employer profile
        employer_serializer = EmployerProfileSerializer(instance=employer_profile, data=employer_profile_data, partial=True)
        if employer_serializer.is_valid():
            employer_serializer.save()

            # Serialize the user data
            user_serializer = UserSerializer(request.user)

            # Prepare the response data including user and employer profile
            response_data = {
                "user": user_serializer.data,
            }
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Invalid employer profile data format. Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_employees(request):
    employees = User.objects.filter(user_type="employee")
    serializer = UserSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_employers(request):
    employers = User.objects.filter(user_type="employer")
    serializer = UserSerializer(employers, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, id):
    user = User.objects.filter(id=id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request):
    services = Service.objects.all()  # Fetch all services
    serializer = ServiceSerializer(services, many=True)  # Serialize the services
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_search(request):
    # Check if the user is an employer
    if request.user.user_type != 'employer':
        raise PermissionDenied('Only employers can view this data.')

    # Extract search parameters from the request
    location = request.query_params.get('location', None)
    country = request.query_params.get('country', None)
    service_type = request.query_params.get('service_type', None)
    work_experience = request.query_params.get('work_experience', None)
    salary_expectation = request.query_params.get('salary_expectation', None)

    # Build the search query using Q objects
    query = Q()

    if location:
        query &= Q(location__icontains=location)
    if country:
        query &= Q(country__icontains=country)
    if service_type:
        query &= Q(service_type__id=service_type)
    if work_experience:
        query &= Q(work_experience__icontains=work_experience)

    if salary_expectation:
        # Check if salary_expectation is a range "min-max"
        match = re.match(r"(\d+)-(\d+)", salary_expectation)
        if match:
            min_salary = int(match.group(1))
            max_salary = int(match.group(2))
            query &= Q(salary_expectation__gte=min_salary, salary_expectation__lte=max_salary)
        else:
            # Handle cases where salary_expectation is a single value
            salary_value = int(salary_expectation)
            query &= Q(salary_expectation__icontains=str(salary_value))

            # Handle case where salary is inside a range (e.g., "90000-100000")
            query |= Q(salary_expectation__contains=f"{salary_value}-") | Q(salary_expectation__contains=f"-{salary_value}")

    # Filter the EmployeeProfile based on the query
    employees = EmployeeProfile.objects.filter(query)

    # Serialize the result
    serializer = EmployeeProfileSerializer(employees, many=True)
    
    # Return the response
    return Response(serializer.data)