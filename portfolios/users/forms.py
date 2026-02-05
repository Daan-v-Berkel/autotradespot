from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.forms import CheckboxInput, EmailField
from django.utils.translation import gettext_lazy as _

from portfolios.lease_finder_app.forms import StyledForm, StyledModelForm

from .models import UserCustomisation

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class UserChangeForm(StyledModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "username",
        )
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserPreferenceForm(StyledModelForm):
    class Meta:
        model = UserCustomisation
        exclude = ("user",)
        labels = {
            "marketing_emails": _("recieve marketing emails"),
            "listing_updates": _("recieve listing updates"),
            "favorites_updates": _("recieve updates about favourites"),
            "display_contact_info": _("display contact information publicly"),
        }
        widgets = {
            "marketing_emails": CheckboxInput(attrs={"class": "toggle toggle-success"}),
            "listing_updates": CheckboxInput(attrs={"class": "toggle toggle-success"}),
            "favorites_updates": CheckboxInput(attrs={"class": "toggle toggle-success"}),
            "display_contact_info": CheckboxInput(attrs={"class": "toggle toggle-success"}),
        }
