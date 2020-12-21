from django import forms
from .models import Measurement


class MeasurementModelForm(forms.ModelForm):
    location = forms.CharField(label='Location:', widget=forms.TextInput(
        attrs={'placeholder': 'Please enter your location...'}))

    class Meta:
        model = Measurement
        fields = ('location',)
