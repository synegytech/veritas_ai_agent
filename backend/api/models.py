from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class ModelInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Input from {self.user.username} at {self.created_at}"


class ModelOutput(models.Model):
    input_data = models.ForeignKey(
        ModelInput, on_delete=models.CASCADE, related_name="outputs"
    )
    output_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Output for {self.input_data} at {self.created_at}"
