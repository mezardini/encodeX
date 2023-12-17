from rest_framework import serializers
from .models import EncodedImage


class EncodedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncodedImage
        fields = ['id', 'image', 'message']
