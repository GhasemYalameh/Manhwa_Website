from django.core.files.storage import FileSystemStorage
from config.settings import PROTECTED_MEDIA_ROOT

protected_storage = FileSystemStorage(
    location=PROTECTED_MEDIA_ROOT,
    base_url=None,
)
