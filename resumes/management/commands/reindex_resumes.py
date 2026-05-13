from django.core.management.base import BaseCommand

from resumes.models import Resume
from resumes.services import TextExtractorService
from resumes.services.vector_store import get_default_vector_store


class Command(BaseCommand):
	help = "Re-extracts text and re-indexes all resumes into ChromaDB"

	def handle(self, *args, **opts):
		extractor = TextExtractorService()
		store = get_default_vector_store()
		total = 0
		for resume in Resume.objects.all():
			try:
				# Re-extract text if missing
				if not resume.raw_text:
					resume.raw_text = extractor.extract_from_uploaded(resume.file)
					resume.save(update_fields=["raw_text", "updated_at"])

				# Index into vector store
				chunks = store.index_resume(
					resume_id=str(resume.id),
					text=resume.raw_text,
					metadata={"candidate_name": resume.candidate_name or ""},
				)
				total += chunks
				self.stdout.write(f"  ✓ {resume.id} ({chunks} chunks)")
			except Exception as exc:  # noqa: BLE001
				self.stderr.write(f"  ✗ {resume.id}: {exc}")
		self.stdout.write(self.style.SUCCESS(f"Indexação concluída. Total de chunks: {total}"))
