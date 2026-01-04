from django.db import models
from django.contrib.postgres.fields import ArrayField
from manage import init_django

init_django()


class Context(models.Model):
    class Meta:
        db_table = "aiassistant"

    created_at = models.DateTimeField(auto_now_add=True)
    context = models.TextField()
    created_by = models.CharField(max_length=255)
    tags = ArrayField(
        models.CharField(max_length=255), default=list
    )  # Assuming tags are stored as a comma-separated string

    def __str__(self):
        return f"Context(id={self.id}, created_at={self.created_at}, context={self.context}, created_by={self.created_by})"
