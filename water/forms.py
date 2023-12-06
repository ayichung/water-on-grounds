from django import forms
from .models import WaterStation, Building

# REFERENCE: https://docs.djangoproject.com/en/4.2/ref/forms/fields/

class WaterStationForm(forms.ModelForm):
    class Meta:
        model = WaterStation
        fields = ['building', 'floor', 'cardinal', 'traditional', 'bottle']
        widgets = {
            'floor': forms.TextInput(attrs={
                'min':0,
                'max':10,
                'type':'number',
            }),
            'cardinal': forms.RadioSelect(),
        }
        labels = {
            'building': 'What building is the station located in?',
            'floor':'What floor is the station on? (Enter 0 for basement level)',
            'cardinal':'What area of the floor is the station in?',
            'traditional':'Drinking dispenser',
            'bottle':'Bottle refill dispenser',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    # def clean(self):
    #     clean_data = self.cleaned_data
    #     if not clean_data.get("traditional") and not clean_data.get("bottle"):
    #         raise forms.ValidationError("At least one dispenser type must be selected")
    #     return clean_data

class AdminApprovalForm(forms.ModelForm):
    class Meta:
        model = WaterStation
        fields = ['approved']