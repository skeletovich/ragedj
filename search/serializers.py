from rest_framework import serializers
from .models import Document, Chunk

class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk
        fields = ['id', 'content', 'position']
        read_only_fields = ['id', 'content', 'position']

class DocumentMiniSerializer(serializers.ModelSerializer):
    source_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'source_type', 'source_type_display']
        read_only_fields = ['id', 'title', 'source_type', 'source_type_display']
    
    def get_source_type_display(self, obj):
        return obj.get_source_type_display()

class DocumentListSerializer(serializers.ModelSerializer):
    source_type_display = serializers.SerializerMethodField()
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'source_type', 'source_type_display', 'created_at', 'chunk_count']
        read_only_fields = ['id', 'title', 'source_type', 'source_type_display', 'created_at', 'chunk_count']
    
    def get_source_type_display(self, obj):
        return obj.get_source_type_display()
    
    def get_chunk_count(self, obj):
        # Check if chunk count is annotated (for performance optimization)
        if hasattr(obj, '_chunk_count'):
            return obj._chunk_count
        return obj.chunks.count()

class DocumentDetailSerializer(serializers.ModelSerializer):
    source_type_display = serializers.SerializerMethodField()
    chunks = ChunkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'source_type', 'source_type_display', 'created_at', 'chunks']
        read_only_fields = ['id', 'title', 'source_type', 'source_type_display', 'created_at', 'chunks']
    
    def get_source_type_display(self, obj):
        return obj.get_source_type_display()

class SearchResultSerializer(serializers.ModelSerializer):
    document = DocumentMiniSerializer(read_only=True)
    
    class Meta:
        model = Chunk
        fields = ['id', 'content', 'position', 'document']
        read_only_fields = ['id', 'content', 'position', 'document']
