from django import forms
from .models import PhotoPost, Comment
from django.contrib.auth.models import User


class PhotoPostForm(forms.ModelForm):
    class Meta:
        model = PhotoPost
        fields = ['title', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
