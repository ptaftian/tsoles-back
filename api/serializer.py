

from api.models import User, Bug, Log, AppVersion, Ticket , Examination
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'serial_number']  # Include any additional fields you want

class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = ['id', 'hardwareCode', 'softwareCode', 'bugTxt', 'created_at']

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'hardwareCode', 'softwareCode', 'logTxt', 'created_at']

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ['id', 'version_number', 'file', 'additional_file', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'serial_number']
        extra_kwargs = {
            'phone_number': {'required': False},
            'serial_number': {'required': False},
        }

class TicketSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True) 

    class Meta:
        model = Ticket
        fields = ['id', 'customer_username', 'title', 'body', 'created_at', 'active']  
        extra_kwargs = {
            'customer': {'read_only': True}, 
        }

    def create(self, validated_data):
        customer = validated_data.pop('customer', None)
        ticket = Ticket.objects.create(customer=self.context['request'].user, **validated_data)
        return ticket

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.profile.full_name if user.profile else None
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio if user.profile else None
        token['image'] = str(user.profile.image) if user.profile and user.profile.image else None
        token['verified'] = user.profile.verified if user.profile else None
        return token


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This email is already in use. Please select a different email."
            )
        ]
    )
    
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This username is already taken. Please choose another username."
            )
        ]
    )
    
    serial_number = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This serial number is already in use. Please select a different serial number."
            )
        ]
    )
    
    phone_number = serializers.CharField(required=False)
    
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'serial_number', 'phone_number', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            serial_number=validated_data.get('serial_number'),
            phone_number=validated_data.get('phone_number')
        )

        user.set_password(validated_data['password']) 
        user.save()
        return user


class ExaminationSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Examination
        fields = [
            'id',
            'customer_username',
            'dataset',
            'design_title',
            'last_uid',
            'high_heel',
            'has_shoe',
            'single_foot',
            'download'
        ]

    def validate_download(self, value):
        # Check that the uploaded file is a ZIP file
        if not value.name.endswith('.zip'):
            raise serializers.ValidationError("Only ZIP files are accepted for upload.")
        return value