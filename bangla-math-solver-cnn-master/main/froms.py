from django import forms
from .models import *
  
class handwritingForm(forms.ModelForm):
  
    class Meta:
        model = Handwriting
        fields = ['image']