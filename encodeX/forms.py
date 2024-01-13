from django import forms
from drf_braces.serializers.form_serializer import FormSerializer


class EmailForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=30)


class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=30)
    email = forms.EmailField()


class EncodeImageForm(forms.Form):
    message = forms.CharField(max_length=100)
    image = forms.ImageField()


class DecodeImageForm(forms.Form):
    image = forms.ImageField()

# class CodeSerializer(FormSerializer):
#     class Meta(object):
#         form = CodeVerificationForm
