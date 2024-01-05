from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# Create your models here.


# class User(AbstractBaseUser, PermissionsMixin):
# 		email = models.EmailField(_("email address"), unique=True)
# 		username = models.CharField(_("username"), unique=True, max_length=32)

# 		phone = PhoneNumberField(_("phone number"), null=True, blank=True)
# 		first_name = models.CharField(_("first name"), max_length=32, null=True, blank=True)
# 		last_name = models.CharField(_("last name"), max_length=64, null=True, blank=True)
# 		postal_code = models.CharField(_("postal code"), max_length=8, null=True, blank=True)
# 		house_number = models.CharField(_("house number"), max_length=8, null=True, blank=True)
# 		street = models.CharField(_("street"), max_length=128, null=True, blank=True)
# 		city = models.CharField(_("place of residence"), max_length=128, null=True, blank=True)
# 		is_staff = models.BooleanField(default=False)
# 		is_active = models.BooleanField(default=True)
# 		date_joined = models.DateTimeField(default=timezone.now)

# 		USERNAME_FIELD = "username"
# 		REQUIRED_FIELDS = ["email"]

# 		objects = UserManager()

# 		@property
# 		def full_name(self):
# 			"Returns the user's full name."
# 			if self.usercustomisation.display_name:
# 				return f"{self.first_name} {self.last_name}"

# 		@property
# 		def give_phone(self):
# 			"Returns the user's phone number if allowed."
# 			if self.usercustomisation.display_phone:
# 				return f"{self.phone}"

# 		@property
# 		def give_email(self):
# 			"Returns the user's phone number if allowed."
# 			if self.usercustomisation.display_email:
# 				return f"{self.email}"

# 		@property
# 		def full_adress(self):
# 			"returns the user's full adress string"
# 			if self.usercustomisation.display_adres:
# 				return f"{self.street} {self.house_number}\n{self.postal_code}, {self.city}"

# 		@property
# 		def location(self):
# 			"returns the user's general location"
# 			if self.usercustomisation.display_adres:
# 				return f"{self.city}"

# 		def save(self, *args, **kwargs):
# 			print(f'saving: {kwargs}, {args}')
# 			super().save(*args, **kwargs)

# 		def __str__(self):
# 				return self.email

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
