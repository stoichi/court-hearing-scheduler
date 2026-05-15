from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from datetime import datetime

from accounts.models import User

class CourtHearing(models.Model):
    """A scheduled court hearing with participants and a validated time window."""

    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    participants = models.ManyToManyField(User, related_name="hearings")

    def __str__(self) -> str:
        """
        Build the human-readable label for the hearing.

        Return:
        - The hearing's name
        """
        return self.name

    @classmethod
    def get_conflicting_hearing(cls, target_hearing: "CourtHearing") -> "CourtHearing | None":
        """
        Find another hearing that overlaps the given hearing's date and time window.

        Parameters:
        - target_hearing: the hearing whose schedule is being checked for conflicts

        Return:
        - The first overlapping CourtHearing if one exists
        - None when no other hearing overlaps the target
        """
        return (
            cls.objects.exclude(pk=target_hearing.pk)
            .filter(
                date=target_hearing.date,
                start_time__lt=target_hearing.end_time,
                end_time__gt=target_hearing.start_time,
            )
            .first()
        )

    def clean(self) -> None:
        """
        Validate the hearing's date and time window and reject past or conflicting schedules.
        """
        super().clean()

        if self.date and self.date < timezone.localdate():
            raise ValidationError({"date": "Date can not be in the past."})

        if self.date and self.start_time:
            start_dt = timezone.make_aware(datetime.combine(self.date, self.start_time))
            if start_dt <= timezone.now():
                raise ValidationError({"start_time": "Start time can not be in the past."})

        if self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        conflicting_hearing = CourtHearing.get_conflicting_hearing(target_hearing=self)
        if conflicting_hearing:
            raise ValidationError(
                f"Hearing time conflicts with an existing hearing on {conflicting_hearing.date} from {conflicting_hearing.start_time} to {conflicting_hearing.end_time}."
            )
