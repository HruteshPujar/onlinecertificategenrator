from django.db import models


class Event(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    venue = models.CharField(max_length=200)

    event_date = models.DateField()

    certificate_template = models.ImageField(
    upload_to="templates/",
    blank=True,
    null=True
)
    is_active = models.BooleanField(default=True)

    # Position Settings
    name_x = models.IntegerField(default=0)
    name_y = models.IntegerField(default=0)

    event_x = models.IntegerField(default=0)
    event_y = models.IntegerField(default=0)

    date_x = models.IntegerField(default=0)
    date_y = models.IntegerField(default=0)

    certificate_id_x = models.IntegerField(default=0)
    certificate_id_y = models.IntegerField(default=0)

    # Font Settings
    name_font_size = models.IntegerField(default=60)
    event_font_size = models.IntegerField(default=40)
    date_font_size = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)