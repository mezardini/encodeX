from rest_framework import generics
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import EncodedImage, CustomUser, UserCode
from .serializers import EncodedImageSerializer
from .serializers import EmailSerializer, CodeVerificationSerializer, UserCodeSerializer, DecodeImageSerializer
from PIL import Image
import io
from django.core.files.images import get_image_dimensions
from django.contrib.auth import login, logout
import random
import string
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
import jwt
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.conf import settings
from .generate_token import generate_access_token
import re
from django.core.mail import send_mail


from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.images import get_image_dimensions
import io
from io import BytesIO
from django.core.files.base import ContentFile


import binascii


def encode_image(encoded_image_id):
    # Retrieve the EncodedImage instance from the database
    encoded_image_instance = EncodedImage.objects.get(pk=encoded_image_id)

    # Load the image from the database
    image_data = encoded_image_instance.image.read()

    # Convert the message to hexadecimal
    encode_message_id = str(encoded_image_instance.message_id)
    hex_message = encode_message_id.encode('utf-8').hex()

    # Append the message to the end of the image data
    encoded_data = image_data + bytes.fromhex(hex_message)

    # Create a new image with the combined data
    updated_image = Image.open(BytesIO(encoded_data))

    # Save the updated image data to a new file-like object
    updated_image_data = BytesIO()
    updated_image.save(updated_image_data, format='PNG')
    updated_image_data.seek(0)

    # Update the EncodedImage model with the new content file and message
    encoded_image_instance.image = InMemoryUploadedFile(
        updated_image_data,
        None,
        f'encoded_image_{encoded_image_id}.png',
        'image/png',
        updated_image_data.tell(),
        None
    )

    # Update the message in the model
    encoded_image_instance.message = "New encoded message"

    # Save the changes to the model
    encoded_image_instance.save()

    return encoded_image_instance


def decode_image(encoded_image_data):
    # Open the image
    image = Image.open(BytesIO(encoded_image_data))

    # Extract the message from the last part of the image data
    # Assuming the message is stored in hexadecimal format
    message_length = len(encoded_image_data) // 4
    hex_message_bytes = encoded_image_data[-message_length:]

    # Decode the hexadecimal message to retrieve the original message
    original_message = bytes.fromhex(
        hex_message_bytes.decode('utf-8')).decode('utf-8')

    return original_message



class EncodeImageView(generics.CreateAPIView):

    queryset = EncodedImage.objects.all()
    serializer_class = EncodedImageSerializer

    def perform_create(self, request):
        # serializer = EncodedImageSerializer(data=request.data)
        # if serializer.is_valid():
        image = self.request.data['image']
        message = self.request.data['message']
        image_user = CustomUser.objects.get(email='seb@m.com')
        random_integer = random.randint(10000, 99999)
        encode_image_req = EncodedImage.objects.create(
            image=image, message=message, user=image_user, message_id=random_integer)
        encode_image_req.save()

        # Encode the message in the image
        encoded_image = encode_image(encode_image_req.id)

        user_credit = CustomUser.objects.get(username='mezardini')

        user_credit.credit -= 1
        user_credit.save()

        # Return the encoded image to the client
        return Response({'image': encoded_image}, status=status.HTTP_201_CREATED)


def extract_encoded_hex_from_image(image_data):
    # Check if the image data contains encoded information
    start_marker = b'ENCODED_INFO_START'
    end_marker = b'ENCODED_INFO_END'

    if start_marker in image_data and end_marker in image_data:
        start_index = image_data.find(start_marker) + len(start_marker)
        end_index = image_data.find(end_marker)
        hex_message_bytes = image_data[start_index:end_index]

        # Decode the hexadecimal message to retrieve the original message
        original_message = bytes.fromhex(
            hex_message_bytes.decode('utf-8')).decode('utf-8')
        print(original_message)
        return original_message
    else:
        # If no encoded information is found, return None
        return None


class DecodeImageView(generics.CreateAPIView):
    serializer_class = DecodeImageSerializer
    parser_classes = [MultiPartParser]

    def create(self, request):
        image = request.data.get('image')

        # Ensure 'image' field is present in the request
        if not image:
            return Response({'error': 'Please provide an image for decoding.'}, status=400)

        # Decode the message from the image
        decoded_message = decode_image(image)
        print(decoded_message)

        # # Create a new instance with the decoded message
        # serializer = self.get_serializer(data={'message': decoded_message})
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)

        # headers = self.get_success_headers(serializer.data)
        return Response(decoded_message)


class EmailValidatorandMailSender(generics.CreateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = EmailSerializer

    verification_code = ''.join(random.choices(string.ascii_lowercase, k=5))

    def validate_email(self, email):
        # Check email format with regex
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not re.match(email_pattern, email):
            return False

    def validate_user(self, email, username):
        # check_email = self.validate_email(email)
        # if check_email:
        if CustomUser.objects.filter(email=email).exists():
            return True
        else:
            CustomUser.objects.create(email=email, username=username)
            return True
        # else:
        #     return Response({'message': f'User does not exist.'})

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            is_valid = self.validate_user(email, username)
            if is_valid:
                # send_mail(
                #     'Hello ' + username,
                #     'This is the verification code ' + EmailValidatorandMailSender.verification_code,
                #     'settings.EMAIL_HOST_USER',
                #     [email],
                #     fail_silently=False,
                # )
                verification_code = EmailValidatorandMailSender.verification_code
                user = CustomUser.objects.get(email=email)
                verification_code_save = UserCode.objects.update_or_create(
                    code=verification_code, user=user)
                # verification_code_save.update()
                print(EmailValidatorandMailSender.verification_code)
                return redirect('verifyuser_code')

            else:
                return Response({'message': f'{email} is not a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    pass


class CodeVerification(generics.CreateAPIView):
    serializer_class = CodeVerificationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
            verification_query = UserCode.objects.filter(
                user=user).latest('id')
            verification_code = verification_query.code

            if code == verification_code:

                # Generate and return the access token
                user_token = generate_access_token(email)
                response = Response({'access_token': user_token})
                response.set_cookie(key='access_token',
                                    value=user_token, httponly=True)

                login(request, user)
                return response
            else:
                return Response({'message': 'User is not verified.'}, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        # Customize the data you want to return in the response
        data = {
            'username': user.username,
            'email': user.email,
            'image-credit': user.credit,
            # Add other user details as needed
        }
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        # Log the user out
        logout(request)

        # Clear the access token cookie
        response = Response({'message': 'User logged out successfully.'})
        response.delete_cookie('access_token')

        return response


class BuyCreditView(APIView):
    pass
