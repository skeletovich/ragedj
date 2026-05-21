from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import DocumentListView, DocumentDetailView, SearchView

urlpatterns = [
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("search/", SearchView.as_view(), name="search"),
    path("auth/token/", obtain_auth_token, name="auth-token"),
]
