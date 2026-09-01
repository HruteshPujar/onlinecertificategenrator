from django import forms
from .models import Participant


class ParticipantForm(forms.ModelForm):

    class Meta:

        model = Participant

        fields = [
            "event",
            "full_name",
            "email",
            "phone",
            "college",
            "department",
            "usn",
        ]

        widgets = {

            "event": forms.Select(attrs={
                "class": "form-select"
            }),

            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Full Name"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Phone Number"
            }),

            "college": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "department": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "usn": forms.TextInput(attrs={
                "class": "form-control"
            }),

        }