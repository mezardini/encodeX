from django import forms
from drf_braces.serializers.form_serializer import FormSerializer


class EmailForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=30)


class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=30)
    email = forms.EmailField()


# class CodeSerializer(FormSerializer):
#     class Meta(object):
#         form = CodeVerificationForm
