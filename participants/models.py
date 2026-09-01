from django.db import models
from events.models import Event


class Participant(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    full_name = models.CharField(max_length=200)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    college = models.CharField(max_length=200)

    department = models.CharField(max_length=100)

    usn = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    generated_certificate = models.ImageField(
    upload_to="certificates/",
    blank=True,
    null=True)

    certificate_generated = models.BooleanField(default=False)

    email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name