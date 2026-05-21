from django.urls import path
from .views import DocumentListView, DocumentDetailView

urlpatterns = [
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
]