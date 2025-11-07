from django.db import models
import uuid


class Campaign(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    date_selection_type = models.BooleanField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    data_source = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'

    def __str__(self):
        return self.name



class Market(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'markets'
        indexes = [
            models.Index(fields=['name'], name='idx_market_name'),
        ]

    def __str__(self):
        return self.name


class Format(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'formats'
        indexes = [
            models.Index(fields=['name'], name='idx_formats_name'),
        ]

    def __str__(self):
        return self.name


class Representative(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'representatives'
        indexes = [
            models.Index(fields=['name'], name='idx_representatives_name'),
        ]

    def __str__(self):
        return self.name



from accounts.models import User
from django.utils.text import slugify
# Use the correct user model (custom or default)

class RadioStation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    # slug = models.SlugField(unique=False, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=False, null=False)
    # slug = models.SlugField(unique=True, blank=True)
    market = models.ForeignKey(
        'Market', on_delete=models.SET_NULL, null=True, related_name='radio_stations'
    )
    owner = models.CharField(max_length=255, null=True, blank=True)
    format = models.ForeignKey(
        'Format', on_delete=models.SET_NULL, null=True, related_name='radio_stations'
    )
    station_group = models.CharField(max_length=255, null=True, blank=True)
    rep = models.ForeignKey(
        'Representative', on_delete=models.SET_NULL, null=True, related_name='radio_stations'
    )
    assign_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='assigned_stations'
    )
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'radio_stations'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_radio_station_name'),
        ]
        indexes = [
            models.Index(fields=['assign_user'], name='idx_radio_stations_assign_user'),
            models.Index(fields=['market'], name='idx_radio_stations_market'),
            models.Index(fields=['rep'], name='idx_radio_stations_rep'),
            models.Index(fields=['format'], name='idx_radio_stations_format'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while RadioStation.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
