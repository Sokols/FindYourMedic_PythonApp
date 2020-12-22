from django import forms
from .models import Measurement


class MeasurementModelForm(forms.ModelForm):
    localization = forms.CharField(label='Localization:', widget=forms.TextInput(
        attrs={'placeholder': 'Please enter your localization...'}))

    class Meta:
        model = Measurement
        fields = ('localization',)
