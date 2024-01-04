from celery import shared_task
from django.core.mail import send_mail


@shared_task()
def send_contact_email_task(subject, message, from_email):
    print("sending email from task with changed shit")
    send_mail(
        subject,
        message,
        from_email,
        ["admin@example.com"],
        fail_silently=False,
    )
