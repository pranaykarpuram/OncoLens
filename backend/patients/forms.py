from django import forms

from patients.models import ClinicalNote


class PatientSearchForm(forms.Form):
    q = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Name or MRN"}),
    )


class ClinicalNoteForm(forms.ModelForm):
    """Patient context is enforced in the workspace view."""

    class Meta:
        model = ClinicalNote
        fields = ["note_type", "note_date", "text"]
        widgets = {
            "note_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 6}),
        }
