from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm

# from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# from portfolios.lease_finder_app.models import *
# from portfolios.listings.tasks import send_contact_email_task


class StyledModelForm(ModelForm):
    template_name_div = "../templates/forms/custom_div.html"
    template_name_p = "../templates/forms/as_p_faker.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, (forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({"class": "checkbox checkbox-accent"})
            elif isinstance(field, (forms.TypedChoiceField, forms.ModelChoiceField, forms.ChoiceField)) or isinstance(
                field.widget, forms.Select
            ):
                field.widget.attrs.update({"class": "select select-bordered select-sm w-full max-w-xs"})
            elif isinstance(field.widget, (forms.Textarea)):
                field.widget.attrs.update({"class": "textarea textarea-bordered w-full max-w-xs"})
            else:
                field.widget.attrs.update({"class": "input input-bordered input-sm w-full max-w-xs", "size": 40})


class StyledForm(forms.Form):
    template_name_div = "../templates/forms/custom_div.html"
    template_name_p = "../templates/forms/as_p_faker.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({"class": "checkbox checkbox-accent"})
            elif isinstance(field, (forms.TypedChoiceField, forms.ChoiceField, forms.ModelChoiceField)) or isinstance(
                field.widget, forms.Select
            ):
                field.widget.attrs.update({"class": "select select-bordered select-sm w-full max-w-xs"})
            elif isinstance(field.widget, (forms.Textarea)):
                field.widget.attrs.update({"class": "textarea textarea-bordered w-full max-w-xs"})
            else:
                field.widget.attrs.update({"class": "input input-bordered input-sm w-full max-w-xs", "size": 40})


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    template_name = "../templates/widgets/image_select.html"


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class LoginForm(AuthenticationForm, StyledForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "p-1 rounded-lg block w-full border-2"}), label=_("username or email")
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "p-1 rounded-lg block w-full border-2"}))
