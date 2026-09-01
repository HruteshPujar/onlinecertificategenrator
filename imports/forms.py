from django import forms
from events.models import Event


class ExcelUploadForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(is_active=True).order_by("-id"),
        required=True,
        empty_label="-- Select Target Event --",
        widget=forms.Select(attrs={"class": "form-select", "required": True})
    )

    file = forms.FileField(
        label="Select Excel / CSV File",
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx, .xls, .csv",
            "required": True,
        })
    )