from django import forms
from django.conf import settings


class SubmissionForm(forms.Form):
    language = forms.ChoiceField(
        label="Language",
        choices=settings.SUBMISSION_LANGUAGES,
    )

    source_file = forms.FileField(
        label="Source file",
        allow_empty_file=False,
    )

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get("source_file")

        if source is None:
            return

        limit = settings.SUBMISSION_MAX_BYTES
        if source.size > limit:
            self.add_error("source_file", "File exceeds size limit.")
            return

        cleaned["source_code"] = source.read()
        return cleaned
