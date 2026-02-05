from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from portfolios.users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Portfolios.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("name"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    phone = PhoneNumberField(_("Phone number"), blank=True)
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username, (displayed to other users)"), blank=True, max_length=60)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail")


class UserCustomisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    marketing_emails = models.BooleanField(default=False)
    listing_updates = models.BooleanField(default=False)
    favorites_updates = models.BooleanField(default=False)
    display_contact_info = models.BooleanField(default=False)

    def __str__(self):
        return f"user customisation for {self.user.email}"


# create preferences for each created user
@receiver(post_save, sender=User)
def createUserPreferences(sender, instance, created, **kwargs):
    if created:
        UserCustomisation.objects.create(user=instance)
