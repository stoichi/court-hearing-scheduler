from django import forms

from .models import CourtHearing


class CourtHearingForm(forms.ModelForm):
    """ModelForm for creating and editing court hearings."""

    class Meta:
        model = CourtHearing
        fields = ["name", "description", "date", "start_time", "end_time", "participants"]
        widgets = {
            "name": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 3}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "participants": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # User.__str__ reads self.role so fetch the data to improve performance by limiting unneeded queries
        self.fields["participants"].queryset = (                        # type: ignore  queryset is a member of the field
            self.fields["participants"].queryset.select_related("role") # type: ignore  queryset is a member of the field
        )
