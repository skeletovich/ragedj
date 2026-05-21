# ragedj — Django + DRF demo project

## What this is

A one-evening Django + DRF side project that replicates a small slice of a production FastAPI app ([Ragepsteiner](https://ragepsteiner.space)) in Django, to demonstrate Django/DRF competence to a hiring team. Production version is on FastAPI + Postgres + pgvector + Claude streaming over ~1,650 chunks of declassified court documents, FBI FOIA files, and handwritten flight logs. This demo intentionally keeps only the **mechanical core** — models, endpoints, auth, admin, tests — and skips the AI layer entirely.

## Goal

Build a runnable, tested, documented Django + DRF REST API in ~5 hours of work, with a clean commit history a reviewer can read top-to-bottom.

## Scope (in / out)

**In scope:**
- Two models: `Document`, `Chunk` (with FK)
- Django migrations
- DRF serializers
- Three REST endpoints: list documents, document detail (with chunks), search chunks by keyword
- Django admin registration for both models
- DRF TokenAuthentication on the search endpoint only
- Token-issuing endpoint (`/api/auth/token/`)
- Unit tests covering: list, detail, search hit, search miss, 401 unauthenticated
- README with setup, endpoints, curl examples, screenshots

**Out of scope (do not build):**
- Embeddings, vector search, pgvector — keyword search only (`Q(content__icontains=query)`)
- Claude / OpenAI / any LLM
- Streaming responses (SSE)
- Frontend
- Postgres (SQLite is fine — this is a Django demo, not a DB demo)
- Stripe / payments
- Docker (Django dev server is fine)
- CI/CD pipeline
- Async views (regular sync views, unless explicitly requested at the end as a bonus)

If a step seems to push toward scope creep, stop and stay minimal. The point is **Django literacy**, not feature richness.

## Stack

- Python 3.11+
- Django 5.x
- Django REST Framework 3.15+
- SQLite (built-in)

## Project layout (current)

```
ragedj/
├── manage.py
├── requirements.txt
├── AGENT.md             # this file
├── README.md            # to be written last
├── .gitignore
├── ragedj/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── search/              # the only app
    ├── models.py
    ├── admin.py
    ├── views.py
    ├── serializers.py   # to be created
    ├── urls.py          # to be created
    ├── tests.py
    └── migrations/
```

## Data model

```python
# search/models.py
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
```

## Endpoints

| Method | Path | Auth | Returns |
|--------|------|------|---------|
| GET | `/api/documents/` | open | paginated list of documents (id, title, source_type, created_at, chunk count) |
| GET | `/api/documents/<id>/` | open | document detail + nested chunks |
| POST | `/api/search/` | TokenAuthentication required | body: `{"query": "..."}` → chunks where `content` icontains query, with document info |
| POST | `/api/auth/token/` | open | DRF's `obtain_auth_token` — body: `{"username", "password"}` → `{"token": "..."}` |

## Commit plan

Each step is one commit. Use these messages verbatim (clear history matters for the reviewer):

1. `Initial Django project setup with DRF dependency` ← already done
2. `Add Document and Chunk models with migrations`
3. `Register Document and Chunk in Django admin`
4. `Add DRF serializers for documents and chunks`
5. `Add list and detail endpoints for documents`
6. `Add keyword search endpoint`
7. `Add DRF TokenAuthentication for search endpoint`
8. `Add unit tests for endpoints and authentication`
9. `Add README with setup instructions and curl examples`

Do not squash. Do not commit half-finished work. If a step breaks tests, fix before committing.

## Coding conventions

- **Match Django idioms.** `urls.py` per app, included in project `urls.py` under `/api/`. ViewSets are fine but plain `APIView` / generics are also fine — pick whichever is clearer per endpoint.
- **DRF serializers do validation.** Don't validate in views.
- **Models do business rules via `Meta` and methods.** Not in views.
- **Tests use `APITestCase`** from `rest_framework.test`, not `django.test.TestCase`, because we're testing API responses.
- **Token auth only on `/api/search/`.** The list/detail endpoints stay open. Don't gate everything — that would obscure the auth demo.
- **No magic.** Use stock DRF generics (`ListAPIView`, `RetrieveAPIView`, `APIView`). No custom mixins, no metaclass tricks.

## Things to definitely include in `settings.py`

- Add `"rest_framework"`, `"rest_framework.authtoken"`, `"search"` to `INSTALLED_APPS`
- Add `REST_FRAMEWORK = {"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 10}` for list endpoint pagination
- `authtoken` app requires its own migration — run `python manage.py migrate` after adding it

## How to seed test data

After models are migrated, give the reviewer (and the author) a way to seed sample data fast. Add a Django management command at `search/management/commands/seed.py` that creates 3 documents with 2-3 chunks each. Use realistic-sounding (but invented) titles like:
- "Court Docket No. 24-1872 — Sealed Filing" (court)
- "FBI FOIA Release MJ-2019-447" (foia)
- "Pilot Logbook Entry, 1995-03-12" (flight_log)

And chunk content that mentions distinctive keywords (e.g. "the witness testified", "redacted under 5 USC 552(b)(7)", "departure: West Palm Beach") so the search endpoint has something interesting to find.

Run with: `python manage.py seed`

## README requirements

The README is the second-most-important artifact after working code. It must contain:

1. **One-line description** — "Django + DRF demo project: REST API over a small document corpus, built as a learning exercise to mirror production FastAPI work."
2. **Why this exists** — one paragraph: "Production version of this concept runs on FastAPI at ragepsteiner.space. This project re-implements the read-side mechanics in Django + DRF to demonstrate framework portability."
3. **Setup** — clone, venv, pip install, migrate, createsuperuser, seed, runserver. Copy-pasteable.
4. **Endpoints** — table from the AGENT.md, with one `curl` example per endpoint.
5. **One screenshot** of the Django admin page showing a Document + its Chunks. (PNG in `docs/admin.png`, referenced from README.)
6. **Architecture notes** — short comparison: FastAPI vs Django + DRF. Three or four bullets, not an essay. Honest observations made *during* the build (e.g. "Django admin is a feature; FastAPI has nothing equivalent without third-party libs", "DRF serializers are more declarative than Pydantic + manual responses").

## What NOT to do

- Do not invent features beyond the scope list above.
- Do not refactor working code "for cleanliness" — ship the minimum.
- Do not skip tests, even if pressed for time. **Cut features before cutting tests.**
- Do not write commit messages like "wip", "fix", "update". Use the planned messages.
- Do not push to GitHub until the README and tests are in place. The first impression of the repo is its top page.