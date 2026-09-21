try:
    import magic
except ImportError:  # pragma: no cover - Windows environments may not have libmagic installed.
    magic = None

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def validate_pdf(file):
    """
    Validate uploaded resumes without depending on a system libmagic installation.
    We still enforce the PDF extension and size, and then verify the file header
    is a valid PDF signature. If python-magic is available, we also use it as an
    extra MIME check.
    """

    # Maximum allowed size (5 MB)
    max_size = 5 * 1024 * 1024

    # Check file size
    if file.size > max_size:
        raise ValidationError("File size must be 5 MB or less.")

    sample = file.read(2048)
    file.seek(0)

    if not sample:
        raise ValidationError("Uploaded file is not a valid PDF.")

    if sample.startswith(b"%PDF"):
        return

    if magic is not None:
        mime = magic.from_buffer(sample, mime=True)
        if mime == "application/pdf":
            return

    raise ValidationError("Uploaded file is not a valid PDF.")


class CareerApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField(blank=True)
    resume = models.FileField(
        upload_to="resumes/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"]), validate_pdf],
    )
    cover_letter = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
