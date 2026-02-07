import logging

from django.core.mail import send_mail

from config import celery_app
from config.settings.base import ADMINS

logger = logging.getLogger(__name__)


@celery_app.task()
def send_contact_email_task(subject, message, from_email, to_email):
    logger.info("sending contact email task to %s", to_email)
    send_mail(
        subject,
        message,
        from_email,
        to_email,
        fail_silently=False,
    )


@celery_app.task()
def send_review_mail_task(listing):
    logger.info("scheduling review mail for listing %s", listing.pk)
    send_mail(
        "review listing",
        f"Please review my listing for activation\nlisting_key: {listing.get_absolute_url()}",
        f"{listing.owner.email}",
        [admin[-1] for admin in ADMINS],
        fail_silently=False,
    )
