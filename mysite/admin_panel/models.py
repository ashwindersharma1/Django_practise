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


import uuid
from django.db import models
 # replace with the correct import


class Schedule(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    date_selection_type = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()
    target_radio_station = models.ForeignKey(
        'RadioStation',  # assuming you already have this model
        on_delete=models.CASCADE,
        null=True,
        db_column='target_radio_station',
        related_name='schedules'
    )
    early_payment_discount = models.BooleanField(default=False)
    goal_cpm = models.FloatField(null=True, blank=True)
    additional_daypart_uuid = models.TextField(null=True, blank=True)
    additional_length = models.IntegerField(null=True, blank=True)
    additional_spots_per_week = models.IntegerField(null=True, blank=True)
    additional_product = models.TextField(null=True, blank=True)
    no_count_weeks = models.FloatField(null=True, blank=True)
    no_discount_amount = models.FloatField(null=True, blank=True)
    total_spots_per_week = models.IntegerField(null=True, blank=True)
    total_spots = models.IntegerField(null=True, blank=True)
    final_total = models.FloatField(null=True, blank=True)
    total_aqh = models.FloatField(null=True, blank=True)
    total_cpm = models.FloatField(null=True, blank=True)
    total_nc_discount = models.FloatField(null=True, blank=True)
    total_epd_discount = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_column='user_id',
        related_name='schedules_for_user'
    )

    schedule_status = models.TextField(default='Draft')  # enum alternative
    partially_filled = models.BooleanField(null=True, blank=True)
    schedule_cpm = models.FloatField(null=True, blank=True)
    toggle_button_status = models.BooleanField(null=True, blank=True)
    epd_cpm = models.FloatField(null=True, blank=True)
    user_draft = models.JSONField(null=True, blank=True)
    additional_day_specific = models.BooleanField(default=False)

    class Meta:
        db_table = "schedules"

    def __str__(self):
        return f"{self.name} ({self.schedule_status})"
