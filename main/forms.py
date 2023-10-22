from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Session
from .models import Photo
from django.core.exceptions import ValidationError
from PIL import Image


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'password']


class PrivateSessionForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'session']
        widgets = {
            'image': forms.ClearableFileInput(attrs={"allow_multiple_selected": True}),
        }

    #def clean_image(self):
    #    image = self.cleaned_data.get('image')

    #    if image:
    #        if not image.name.endswith('.jpg') and not image.name.endswith('.jpeg') and not image.name.endswith('.JPG'):
    #            raise ValidationError('Picture need to be in JPEG.')
    #        try:
    #            img = Image.open(image)
    #            if img.format.lower() != 'jpeg':
    #                raise ValidationError('This is not JPEG.')
    #        except Exception as e:
    #            raise ValidationError('Cannot open file as JPEG.')

    #    return image