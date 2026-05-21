from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Document, Chunk
from .serializers import DocumentListSerializer, DocumentDetailSerializer, SearchResultSerializer

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.annotate(_chunk_count=Count("chunks")).order_by("-created_at")
    serializer_class = DocumentListSerializer

class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer

class SearchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query", "").strip()
        
        if not query:
            return Response(
                {"error": "query is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(query) < 2:
            return Response(
                {"error": "query must be at least 2 characters"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        qs = Chunk.objects.filter(content__icontains=query).select_related("document")
        total = qs.count()
        chunks = qs[:50]
        
        serializer = SearchResultSerializer(chunks, many=True)
        
        return Response({
            "query": query,
            "total_matches": total,
            "returned": len(serializer.data),
            "capped_at": 50,
            "results": serializer.data
        })