import os

from django.core.exceptions import ValidationError

from .constants import SUPPORTED_EXTENSIONS


def validate_excel_file(file):

    extension = os.path.splitext(
        file.name
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValidationError(
            "Only Excel or CSV files are allowed."
        )