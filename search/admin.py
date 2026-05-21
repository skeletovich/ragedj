from django.contrib import admin
from .models import Document, Chunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_type', 'created_at']
    list_filter = ['source_type', 'created_at']
    search_fields = ['title']

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ['position', 'document', 'content']
    list_filter = ['document']
    search_fields = ['content']