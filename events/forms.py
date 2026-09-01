from django import forms
from .models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event

        fields = [
            "title",
            "description",
            "venue",
            "event_date",
            "certificate_template",
            "name_x",
            "name_y",
            "event_x",
            "event_y",
            "date_x",
            "date_y",
            "certificate_id_x",
            "certificate_id_y",
            "name_font_size",
            "event_font_size",
            "date_font_size",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Python Bootcamp 2026",
                "required": True,
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Brief description of the event...",
            }),
            "venue": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g., Main Auditorium / Online",
                "required": True,
            }),
            "event_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
                "required": True,
            }),
            "certificate_template": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "name_x": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "name_y": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "event_x": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "event_y": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "date_x": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "date_y": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "certificate_id_x": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "certificate_id_y": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "name_font_size": forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "150"}),
            "event_font_size": forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "100"}),
            "date_font_size": forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "80"}),
        }
        help_texts = {
            "name_x": "X-coordinate for Name (0 for auto-center)",
            "name_y": "Y-coordinate for Name (0 for default)",
            "certificate_template": "Optional: Upload high-res PNG/JPG template. A default template is generated if empty.",
        }