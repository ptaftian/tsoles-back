from api.models import User, Bug, Log , AppVersion
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = ['id', 'hardwareCode', 'softwareCode', 'bugTxt' , 'created_at']

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'hardwareCode', 'softwareCode', 'logTxt', 'created_at']

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ['id', 'version_number', 'file', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'serial_number']  # Include fields you wish to expose
        extra_kwargs = {
            'phone_number': {'required': False},
            'serial_number': {'required': False},
            # Set other fields to be required or not as per your needs
        }

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # These are claims, you can add custom claims
        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        token['image'] = str(user.profile.image)
        token['verified'] = user.profile.verified
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'serial_number', 'phone_number', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            serial_number=validated_data['serial_number'],
            phone_number=validated_data['phone_number']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user