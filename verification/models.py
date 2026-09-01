from django.db import models

from participants.models import Participant


class CertificateVerification(models.Model):

    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE
    )

    verification_code = models.CharField(
        max_length=100,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.verification_code