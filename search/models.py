from django.db import models

class Document(models.Model):
    SOURCE_TYPES = [
        ("court", "Court Document"),
        ("foia", "FBI FOIA"),
        ("flight_log", "Flight Log"),
    ]
    title = models.CharField(max_length=300)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_source_type_display()}: {self.title}"
class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["document_id", "position"]

    def __str__(self):
        return f"Chunk #{self.position} of {self.document.title[:40]}"