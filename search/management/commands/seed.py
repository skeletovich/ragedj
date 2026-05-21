from django.core.management.base import BaseCommand
from django.db import transaction
from search.models import Document, Chunk


class Command(BaseCommand):
    help = "Seed the database with sample documents and chunks for demo and manual testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing documents and chunks before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            deleted_chunks, _ = Chunk.objects.all().delete()
            deleted_docs, _ = Document.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Reset: deleted {deleted_docs} documents and {deleted_chunks} chunks."
                )
            )

        seed_data = [
            {
                "title": "Court Docket No. 24-1872 — Sealed Filing",
                "source_type": "court",
                "chunks": [
                    "The witness testified under oath that the defendant was present at the meeting on the night in question.",
                    "Counsel for the plaintiff moved to admit Exhibit 14, a series of handwritten notes recovered from the defendant's residence.",
                    "The court reserved judgment on the motion to dismiss pending further evidentiary hearings scheduled for the following month.",
                ],
            },
            {
                "title": "FBI FOIA Release MJ-2019-447",
                "source_type": "foia",
                "chunks": [
                    "Portions of this document have been redacted under 5 USC 552(b)(7)(C) to protect the privacy of third parties.",
                    "Special Agent reports note multiple unscheduled visits to the subject's residence over a six-week observation period.",
                ],
            },
            {
                "title": "Pilot Logbook Entry, 1995-03-12",
                "source_type": "flight_log",
                "chunks": [
                    "Departure: West Palm Beach International, 0742 local. Manifest filed with two passengers and pilot.",
                    "Weather: scattered cumulus at 4000ft, visibility unrestricted, winds 240 at 8 knots.",
                    "Arrival: Teterboro, 1054 local. No anomalies during transit; standard handoff to ground control.",
                ],
            },
        ]

        created_docs = 0
        created_chunks = 0

        for doc_data in seed_data:
            doc, doc_created = Document.objects.get_or_create(
                title=doc_data["title"],
                defaults={"source_type": doc_data["source_type"]},
            )
            if doc_created:
                created_docs += 1

            for position, content in enumerate(doc_data["chunks"]):
                _, chunk_created = Chunk.objects.get_or_create(
                    document=doc,
                    position=position,
                    defaults={"content": content},
                )
                if chunk_created:
                    created_chunks += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_docs} new documents and {created_chunks} new chunks."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total in database: {Document.objects.count()} documents, {Chunk.objects.count()} chunks."
            )
        )