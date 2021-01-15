from django import forms
from .models import Measurement


class MeasurementModelForm(forms.ModelForm):
    CONTENT_TYPE_CHOICES = [('medic', 'Medical team'), ('station', 'Air quality station')]
    PATH_TYPE_CHOICES = [('line', 'Straight line'), ('route', 'Full route')]

    content_type = forms.ChoiceField(label='What do you want to find?',
                                     choices=CONTENT_TYPE_CHOICES, required=False)
    path_type = forms.ChoiceField(label='What should the marked route look like?',
                                  choices=PATH_TYPE_CHOICES, required=False)
    localization = forms.CharField(label='What is your location?', widget=forms.TextInput(
        attrs={'placeholder': 'Please enter your localization...'}))

    class Meta:
        model = Measurement
        fields = ('content_type', 'path_type', 'localization',)
