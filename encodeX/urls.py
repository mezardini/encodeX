from django.urls import path
from .views import EncodeImageView, DecodeImageView, EmailValidatorandMailSender, CodeVerification, DashboardView, LogoutView

urlpatterns = [
    path('encodeimage/', EncodeImageView.as_view(), name='encode_image'),
    path('decodeimage/', DecodeImageView.as_view(), name='decode_image'),
    path('verifyuser/', EmailValidatorandMailSender.as_view(), name='verify_code'),
    path('verifyusercode/', CodeVerification.as_view(), name='verifyuser_code'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
