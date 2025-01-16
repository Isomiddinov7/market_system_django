from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer
    )
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                token = RefreshToken.for_user(user)
                return Response({"access_token": str(token.access_token)},
                                status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    @swagger_auto_schema(responses={200: UserProfileSerializer})
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
