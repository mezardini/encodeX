from rest_framework import generics
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import EncodedImage, CustomUser, UserCode
from .serializers import EncodedImageSerializer
from .serializers import EmailSerializer, CodeVerificationSerializer, UserCodeSerializer
from PIL import Image
from django.contrib.auth import login
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


def encode_image(image, message):

    img = Image.open(image)

    # Convert the message to hexadecimal
    hex_message = message.encode('utf-8').hex()

    # Ensure the image has enough space to store the message
    if len(hex_message) > img.width * img.height:
        raise ValueError("Message is too long for the given image size.")

    # Encode the message in the least significant bit (LSB) of each pixel
    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(img.getpixel((x, y)))
            for i in range(3):  # Iterate over RGB channels
                if data_index < len(hex_message):
                    pixel[i] = pixel[i] & ~1 | int(hex_message[data_index])
                    data_index += 1
            img.putpixel((x, y), tuple(pixel))

    # Return the encoded image
    return img


def decode_image(img):
    # Convert the image to grayscale for simplicity
    img = img.convert('L')

    binary_message = ""
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            binary_message += str(pixel & 1)

    # Convert binary message to characters
    message = ''.join(chr(int(binary_message[i:i + 8], 2))
                      for i in range(0, len(binary_message), 8))
    return message


class EncodeImageView(generics.CreateAPIView):
    queryset = EncodedImage.objects.all()
    serializer_class = EncodedImageSerializer

    def perform_create(self, serializer):
        image = self.request.data['image']
        message = self.request.data['message']

        # Encode the message in the image
        encoded_image = encode_image(image, message)

        user_credit = CustomUser.objects.get(username='mezardini')

        user_credit.credit -= 1
        user_credit.save()

        # Return the encoded image to the client
        return Response({'image': encoded_image}, status=status.HTTP_201_CREATED)


class DecodeImageView(generics.CreateAPIView):
    queryset = EncodedImage.objects.all()
    serializer_class = EncodedImageSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        image = request.data.get('image')

        # Ensure 'image' field is present in the request
        if not image:
            return Response({'error': 'Please provide an image for decoding.'}, status=400)

        # Decode the message from the image
        decoded_message = decode_image(image)

        # Create a new instance with the decoded message
        serializer = self.get_serializer(data={'message': decoded_message})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


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
        # else:
        #     return Response({'message': f'User does not exist.'})

    # def verify_code(self, request, verification_code, email):
    #     serializer = CodeVerificationSerializer(data=request.data)
    #     if serializer.is_valid():
    #         code = serializer.validated_data.get('code')
    #         if code == verification_code:
    #             user_token = generate_access_token(email)
    #             response = Response()
    #             response.set_cookie(key='access_token',
    #                                 value=user_token, httponly=True)
    #             response.data = {
    #                 'access_token': user_token
    #             }
    #             print(response.data)
    #             return Response({'message': f'User is verified.'}, response, status=status.HTTP_200_OK)
    #         else:
    #             return Response({'message': f'User is not verified.'}, status=status.HTTP_400_BAD_REQUEST)

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


# class RegisterUser(APIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = EmailSerializer


class CodeVerification(generics.CreateAPIView):

    serializer_class = CodeVerificationSerializer

    def post(self, request):
        # serializer = CodeVerificationSerializer(data=request.data)
        # if serializer.is_valid():

        code = self.request.data['code']
        email = self.request.data['email']
        user = CustomUser.objects.get(email=email)
        verification_query = UserCode.objects.filter(
            user=user).latest('id')
        verification_code = verification_query.code
        if code == verification_code:
            user_token = generate_access_token(email)
            response = Response()
            response.set_cookie(key='access_token',
                                value=user_token, httponly=True)
            response.data = {
                'access_token': user_token
            }
            print(response.data)
            return Response(response.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': f'User is not verified.'}, status=status.HTTP_400_BAD_REQUEST)

        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuyReceipt(APIView):
    pass
