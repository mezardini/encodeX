from drf_braces.forms.serializer_form import SerializerForm
from rest_framework import serializers
from .models import EncodedImage, UserCode
from django import forms
from drf_braces.serializers.form_serializer import FormSerializer


class EncodedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncodedImage
        fields = ['id', 'image', 'message', 'user']


class UserCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCode
        fields = ['code', 'user']


class EncodeImageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100)
    image = serializers.ImageField()


class EncodeImageForm(SerializerForm):
    class Meta(object):
        serializer = EncodeImageSerializer


class EmailSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    email = serializers.EmailField()


class EmailForm(SerializerForm):
    class Meta(object):
        serializer = EmailSerializer


class CodeVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    email = serializers.EmailField()


class CodeVerificationForm(SerializerForm):
    class Meta(object):
        serializer = CodeVerificationSerializer
