from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Chunk, Document


class DocumentListEndpointTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.doc_old = Document.objects.create(title="Older Doc", source_type="court")
        cls.doc_new = Document.objects.create(title="Newer Doc", source_type="foia")
        now = timezone.now()
        Document.objects.filter(pk=cls.doc_old.pk).update(created_at=now - timedelta(days=1))
        Document.objects.filter(pk=cls.doc_new.pk).update(created_at=now)
        Chunk.objects.create(document=cls.doc_old, content="first chunk", position=0)
        Chunk.objects.create(document=cls.doc_old, content="second chunk", position=1)
        Chunk.objects.create(document=cls.doc_new, content="only chunk", position=0)

    def test_list_returns_200_and_paginated_structure(self):
        response = self.client.get(reverse("document-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_list_includes_chunk_count(self):
        response = self.client.get(reverse("document-list"))
        result = next(r for r in response.data["results"] if r["id"] == self.doc_old.pk)
        self.assertEqual(result["chunk_count"], 2)

    def test_list_orders_by_created_at_desc(self):
        response = self.client.get(reverse("document-list"))
        ids = [r["id"] for r in response.data["results"]]
        self.assertEqual(ids[0], self.doc_new.pk)
        self.assertEqual(ids[1], self.doc_old.pk)


class DocumentDetailEndpointTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.doc = Document.objects.create(title="Detail Doc", source_type="flight_log")
        Chunk.objects.create(document=cls.doc, content="chunk one", position=0)
        Chunk.objects.create(document=cls.doc, content="chunk two", position=1)

    def test_detail_returns_document_with_nested_chunks(self):
        response = self.client.get(reverse("document-detail", args=[self.doc.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.doc.pk)
        self.assertIn("chunks", response.data)
        self.assertEqual(len(response.data["chunks"]), 2)

    def test_detail_returns_404_for_missing_document(self):
        response = self.client.get(reverse("document-detail", args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SearchEndpointTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="searcher", password="pass1234")
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        doc = Document.objects.create(title="Search Doc", source_type="court")
        Chunk.objects.create(document=doc, content="The WITNESS testified under oath", position=0)
        Chunk.objects.create(document=doc, content="No keyword here", position=1)
        Chunk.objects.create(document=doc, content="Witness statement confirmed", position=2)

    def test_search_returns_matching_chunks(self):
        response = self.client.post(reverse("search"), {"query": "witness"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_matches"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_search_is_case_insensitive(self):
        response = self.client.post(reverse("search"), {"query": "WITNESS"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_matches"], 2)

    def test_search_returns_empty_list_when_no_match(self):
        response = self.client.post(reverse("search"), {"query": "xyznonexistent"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_matches"], 0)
        self.assertEqual(response.data["results"], [])

    def test_search_returns_400_when_query_missing(self):
        response = self.client.post(reverse("search"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_returns_400_when_query_empty_string(self):
        response = self.client.post(reverse("search"), {"query": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_returns_400_when_query_too_short(self):
        response = self.client.post(reverse("search"), {"query": "a"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_caps_results_at_50(self):
        doc = Document.objects.create(title="Cap Doc", source_type="foia")
        for i in range(60):
            Chunk.objects.create(document=doc, content=f"capword chunk {i}", position=i)
        response = self.client.post(reverse("search"), {"query": "capword"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_matches"], 60)
        self.assertEqual(response.data["returned"], 50)
        self.assertEqual(response.data["capped_at"], 50)
        self.assertEqual(len(response.data["results"]), 50)


class SearchAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="authuser", password="testpass123")
        self.token, _ = Token.objects.get_or_create(user=self.user)
        doc = Document.objects.create(title="Auth Doc", source_type="court")
        Chunk.objects.create(document=doc, content="auth test content", position=0)

    def test_search_returns_401_without_token(self):
        response = self.client.post(reverse("search"), {"query": "auth"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_returns_401_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtokenvalue")
        response = self.client.post(reverse("search"), {"query": "auth"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_succeeds_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(reverse("search"), {"query": "auth"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_endpoint_returns_token_for_valid_credentials(self):
        response = self.client.post(
            reverse("auth-token"),
            {"username": "authuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_token_endpoint_returns_400_for_invalid_credentials(self):
        response = self.client.post(
            reverse("auth-token"),
            {"username": "authuser", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
