import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ModelAsset, UserProfile


ALLOWED_EXTS = {'.glb', '.gltf', '.zip'}
DEFAULT_MAX_SIZE_BYTES = 50 * 1024 * 1024


class UploadAssetForm(forms.Form):
    name = forms.CharField(max_length=200)
    visibility = forms.ChoiceField(choices=ModelAsset.Visibility.choices)
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['accept'] = '.glb,.gltf,.zip'

    def clean_file(self):
        f = self.cleaned_data['file']
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_EXTS:
            raise forms.ValidationError('只允许上传 .glb / .gltf / .zip 文件')

        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', None) or DEFAULT_MAX_SIZE_BYTES
        if getattr(f, 'size', 0) and f.size > max_size:
            raise forms.ValidationError(f'文件过大，最大允许 {max_size // (1024 * 1024)}MB')
        return f


class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, label='用户名')
    email = forms.EmailField(required=False, label='邮箱')
    first_name = forms.CharField(max_length=150, required=False, label='名字')
    last_name = forms.CharField(max_length=150, required=False, label='姓氏')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email': '邮箱',
            'first_name': '名字',
            'last_name': '姓氏',
        }


class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar',)
        labels = {
            'avatar': '头像',
        }
        widgets = {
            'avatar': forms.FileInput(),
        }
