from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    venue = models.CharField(max_length=200)
    event_date = models.DateField()
    certificate_template = models.ImageField(
        upload_to="templates/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)

    # Position Settings (0 = automatic centering)
    name_x = models.IntegerField(default=0, blank=True)
    name_y = models.IntegerField(default=0, blank=True)

    event_x = models.IntegerField(default=0, blank=True)
    event_y = models.IntegerField(default=0, blank=True)

    date_x = models.IntegerField(default=0, blank=True)
    date_y = models.IntegerField(default=0, blank=True)

    certificate_id_x = models.IntegerField(default=0, blank=True)
    certificate_id_y = models.IntegerField(default=0, blank=True)

    # Font Settings
    name_font_size = models.IntegerField(default=60, blank=True)
    event_font_size = models.IntegerField(default=40, blank=True)
    date_font_size = models.IntegerField(default=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title