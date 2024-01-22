from django import forms
from .models import Shop

class ProductUploadForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ('name', 'url',)