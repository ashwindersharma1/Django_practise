from django.db import models

# Create your models here.
import uuid
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    raw_user_meta_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    role = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"  # important: match your Supabase table name
        
    def __str__(self):
        return str(self.name or self.email)
