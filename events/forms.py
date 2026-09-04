from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Brief description of the event (optional)...",
        })
    )

    name_x = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    name_y = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    event_x = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    event_y = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    date_x = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    date_y = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    certificate_id_x = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    certificate_id_y = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}))
    name_font_size = forms.IntegerField(required=False, initial=60, widget=forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "150"}))
    event_font_size = forms.IntegerField(required=False, initial=40, widget=forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "100"}))
    date_font_size = forms.IntegerField(required=False, initial=30, widget=forms.NumberInput(attrs={"class": "form-control", "min": "10", "max": "80"}))

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
        }

    def clean_name_x(self):
        return self.cleaned_data.get("name_x") or 0

    def clean_name_y(self):
        return self.cleaned_data.get("name_y") or 0

    def clean_event_x(self):
        return self.cleaned_data.get("event_x") or 0

    def clean_event_y(self):
        return self.cleaned_data.get("event_y") or 0

    def clean_date_x(self):
        return self.cleaned_data.get("date_x") or 0

    def clean_date_y(self):
        return self.cleaned_data.get("date_y") or 0

    def clean_certificate_id_x(self):
        return self.cleaned_data.get("certificate_id_x") or 0

    def clean_certificate_id_y(self):
        return self.cleaned_data.get("certificate_id_y") or 0

    def clean_name_font_size(self):
        return self.cleaned_data.get("name_font_size") or 60

    def clean_event_font_size(self):
        return self.cleaned_data.get("event_font_size") or 40

    def clean_date_font_size(self):
        return self.cleaned_data.get("date_font_size") or 30