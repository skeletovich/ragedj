from django.urls import path
from .views import DocumentListView, DocumentDetailView, SearchView

urlpatterns = [
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("search/", SearchView.as_view(), name="search"),
]
