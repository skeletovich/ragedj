from rest_framework import generics
from django.db.models import Count
from .models import Document
from .serializers import DocumentListSerializer, DocumentDetailSerializer

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.annotate(_chunk_count=Count("chunks"))
    serializer_class = DocumentListSerializer

class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer
