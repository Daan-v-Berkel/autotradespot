from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserCustomisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_email = models.BooleanField(default=False)
    display_adres = models.BooleanField(default=False)
    display_phone = models.BooleanField(default=False)
    display_name = models.BooleanField(default=False)

    def __str__(self):
        return f"user customisation for {self.user.email}"

## create preferences for each created user
@receiver(post_save, sender=User)
def createUserPreferences(sender, instance, created, **kwargs):
    if created:
        UserCustomisation.objects.create(user=instance)
