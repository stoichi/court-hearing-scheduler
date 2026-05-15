from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import CourtHearing

def _mock_send_email(subject: str, body: str, recipient: str) -> None:
    """
    Print a mock email to stdout in place of dispatching a real message.

    Parameters:
    - subject: email subject line
    - body: email body text
    - recipient: address that would receive the email
    """
    print(f"[MOCK EMAIL] To: {recipient} | Subject: {subject}\n{body}\n")


@receiver(post_save, sender=CourtHearing)
def on_hearing_saved(sender, instance: CourtHearing, created: bool, **kwargs) -> None:
    """
    Notify all participants whenever a hearing is created or updated.

    Parameters:
    - sender: the model class that emitted the signal
    - instance: the hearing that was saved
    - created: True when the hearing was newly created, False on update
    """
    action = "created" if created else "updated"
    subject = f"Hearing {action}: {instance.name}"
    body = f"The hearing '{instance.name}' has been {action}.\nDate: {instance.date} | {instance.start_time} – {instance.end_time}"

    for participant in instance.participants.all():
        _mock_send_email(subject, body, participant.email)


@receiver(post_delete, sender=CourtHearing)
def on_hearing_deleted(sender, instance: CourtHearing, **kwargs) -> None:
    """
    Notify all participants whenever a hearing is deleted.

    Parameters:
    - sender: the model class that emitted the signal
    - instance: the hearing that was deleted
    """
    subject = f"Hearing cancelled: {instance.name}"
    body = f"The hearing '{instance.name}' on {instance.date} has been cancelled."

    for participant in instance.participants.all():
        _mock_send_email(subject, body, participant.email)
