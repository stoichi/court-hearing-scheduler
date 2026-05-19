from datetime import datetime

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, ValidationError

from accounts.serializers import UserSerializer

from .models import CourtHearing


class CourtHearingSerializer(ModelSerializer):
    """Serializes CourtHearing records and validates dates, time windows, and conflicts."""

    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = CourtHearing
        fields = ["id", "name", "description", "date", "start_time", "end_time", "participants"]

    def validate_date(self, value):
        """
        Reject hearing dates that fall before today.

        Parameters:
        - value: the date submitted for the hearing

        Return:
        - The original date when it is today or later
        """
        if value < timezone.localdate():
            raise ValidationError("Date can not be in the past.")
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Validate the hearing's time window and reject past or conflicting schedules.

        Parameters:
        - attrs: the incoming serializer field values

        Return:
        - The validated attrs dictionary, unchanged
        """
        # Validate the fields for the CourtHearing model. This is done within the model itself but these
        # validate commands allow DRF to return invalid before attempting to create the model object
        date = attrs.get("date") or getattr(self.instance, "date", None)
        start_time = attrs.get("start_time") or getattr(self.instance, "start_time", None)
        end_time = attrs.get("end_time") or getattr(self.instance, "end_time", None)

        # Reject hearings where the start time is in the past
        if date and start_time:
            start_dt = timezone.make_aware(datetime.combine(date, start_time))
            if start_dt <= timezone.now():
                raise ValidationError({"start_time": "Start time can not be in the past."})

        # Ensure the end time is after the start time
        if start_time and end_time and start_time >= end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        # Check for overlap with any other hearings
        if date and start_time and end_time:
            conflict_qs = CourtHearing.objects.filter(
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            # When updating an existing hearing, exclude it from its own conflict check
            if self.instance is not None:
                conflict_qs = conflict_qs.exclude(pk=self.instance.pk)
            conflicting_hearing = conflict_qs.first()
            if conflicting_hearing:
                raise ValidationError(
                    f"Hearing time conflicts with an existing hearing on {conflicting_hearing.date} from {conflicting_hearing.start_time} to {conflicting_hearing.end_time}."
                )

        return attrs
