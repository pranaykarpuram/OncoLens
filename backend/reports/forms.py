from django import forms

from evidence.models import Observation
from reports.models import DiagnosticReport


class ReportIntakeForm(forms.ModelForm):
    paste_text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 14, "placeholder": "Paste clinical report text"}),
        required=False,
        label="Report text",
    )

    class Meta:
        model = DiagnosticReport
        fields = ["patient", "report_type", "report_date", "title", "uploaded_file"]
        widgets = {"report_date": forms.DateInput(attrs={"type": "date"})}

    field_order = ["patient", "report_type", "report_date", "title", "uploaded_file", "paste_text"]

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        uploaded = cleaned.get("uploaded_file")
        pasted = (cleaned.get("paste_text") or "").strip()

        text_body = pasted
        fname = getattr(uploaded, "name", "") if uploaded else ""
        if fname.lower().endswith(".txt"):
            try:
                uploaded.seek(0)
                raw_bytes = uploaded.read()
                decoded = raw_bytes.decode(errors="ignore") if isinstance(raw_bytes, bytes) else str(raw_bytes)
                text_body = (text_body + "\n" + decoded.strip()).strip() if pasted else decoded.strip()
                uploaded.seek(0)
            except Exception:
                pass

        if not text_body and not uploaded:
            raise forms.ValidationError(
                "Please upload a file or paste extracted report text pending clinician confirmation."
            )

        report_type_val = cleaned.get("report_type") or "other"
        label = dict(DiagnosticReport.REPORT_TYPES).get(report_type_val, report_type_val)
        rdate = cleaned.get("report_date") or ""
        title_clean = (cleaned.get("title") or "").strip()
        cleaned["computed_title"] = title_clean or f"{label}{(' — ' + str(rdate)) if rdate else ''}".strip()

        cleaned["normalized_text"] = text_body.strip()
        return cleaned


class ObservationConfirmationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ["value_text", "value_number", "unit", "observed_at", "confirmation_status"]
        widgets = {
            "observed_at": forms.DateInput(attrs={"type": "date"}),
            "confirmation_status": forms.Select(),
        }


ObservationConfirmationFormSet = forms.modelformset_factory(
    Observation,
    form=ObservationConfirmationForm,
    extra=0,
)
