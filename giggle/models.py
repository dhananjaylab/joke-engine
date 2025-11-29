from django.db import models

# Create your models here.
from django.db import models

class Joke(models.Model):
    # Increase max_length to allow style tags (e.g. "Cats [dad]")
    query = models.CharField(max_length=100)
    response = models.TextField()
    created_at = models.DateTimeField(
        verbose_name='Created at',
        auto_now_add=True,
    )
    
    def __str__(self):
        return f"{self.query} - {self.created_at}"
        