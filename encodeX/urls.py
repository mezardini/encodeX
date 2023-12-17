from django.urls import path
from .views import EncodeImageView, DecodeImageView

urlpatterns = [
    path('encodeimage/', EncodeImageView.as_view(), name='encode_image'),
    path('decodeimage/', DecodeImageView.as_view(), name='decode_image'),
]
