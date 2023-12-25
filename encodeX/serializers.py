from rest_framework import serializers
from .models import EncodedImage


class EncodedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncodedImage
        fields = ['id', 'image', 'message']


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)


class CodeVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)
