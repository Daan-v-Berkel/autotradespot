from django.core.mail import send_mail

from config import celery_app


@celery_app.task()
def send_contact_email_task(subject, message, from_email, to_email):
    print("sending email from task with changed shit")
    send_mail(
        subject,
        message,
        from_email,
        to_email,
        fail_silently=False,
    )
