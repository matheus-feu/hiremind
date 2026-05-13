"""Signals: cleanup vector store entries when a Resume is deleted."""
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Resume
from .services.vector_store import get_default_vector_store


@receiver(post_delete, sender=Resume)
def remove_from_vector_store(sender, instance: Resume, **kwargs):
    try:
        get_default_vector_store().remove_resume(str(instance.id))
    except Exception:  # noqa: BLE001
        pass

