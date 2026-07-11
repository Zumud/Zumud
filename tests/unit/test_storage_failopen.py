"""Contract tests for the storage fail-open invariant.

Supabase Storage is an optional write-only archive: with no configuration (or
a failing upload) every storage call must return False without raising, and
the calling feature continues.
"""

from unittest.mock import patch

from backend.core import storage_service as storage_module
from backend.core.storage_service import StorageService, safe_upload_with_fallback


def make_disabled_service() -> StorageService:
    service = StorageService.__new__(StorageService)
    service.supabase = None
    return service


class TestDisabledService:
    def test_not_available(self):
        assert make_disabled_service().is_available() is False

    def test_upload_file_returns_false(self):
        assert make_disabled_service().upload_file("x/y.pdf", b"%PDF") is False

    def test_upload_original_resume_returns_false(self):
        assert make_disabled_service().upload_original_resume(1, b"%PDF") is False


class TestSafeUploadWithFallback:
    def test_skips_when_service_unavailable(self):
        with patch.object(storage_module, "storage_service", make_disabled_service()):
            assert safe_upload_with_fallback(lambda: True) is False

    def test_swallows_upload_exceptions(self):
        available = make_disabled_service()
        available.supabase = object()  # looks available; the upload itself fails

        def exploding_upload():
            raise RuntimeError("network down")

        with patch.object(storage_module, "storage_service", available):
            assert safe_upload_with_fallback(exploding_upload) is False
