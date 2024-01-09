from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.forms import ModelForm
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from portfolios.lease_finder_app.models import *
from portfolios.listings.tasks import send_contact_email_task


class StyledModelForm(ModelForm):
    template_name_div = "../templates/forms/custom_div.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, (forms.TypedChoiceField, forms.ModelChoiceField)):
                field.widget.attrs.update({"class": "select select-bordered select-sm w-full max-w-xs"})
            elif isinstance(field.widget, (forms.Textarea)):
                field.widget.attrs.update({"class": "textarea textarea-bordered w-full max-w-xs"})
            else:
                field.widget.attrs.update({"class": "input input-bordered input-sm w-full max-w-xs", "size": 40})


class StyledForm(forms.Form):
    template_name_div = "../templates/forms/custom_div.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, (forms.TypedChoiceField, forms.ChoiceField)):
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


class UserPreferenceForm(StyledModelForm):
    class Meta:
        model = UserCustomisation
        exclude = ("user",)
        display_email = forms.CharField(
            widget=forms.CheckboxInput(
                attrs={
                    "class": "mr-2 mt-[0.3rem] h-3.5 w-8 appearance-none rounded-[0.4375rem] bg-neutral-300 before:pointer-events-none before:absolute before:h-3.5 before:w-3.5 before:rounded-full before:bg-transparent before:content-["
                    "] after:absolute after:z-[2] after:-mt-[0.1875rem] after:h-5 after:w-5 after:rounded-full after:border-none after:bg-neutral-100 after:shadow-[0_0px_3px_0_rgb(0_0_0_/_7%),_0_2px_2px_0_rgb(0_0_0_/_4%)] after:transition-[background-color_0.2s,transform_0.2s] after:content-["
                    "] checked:bg-primary checked:after:absolute checked:after:z-[2] checked:after:-mt-[3px] checked:after:ml-[1.0625rem] checked:after:h-5 checked:after:w-5 checked:after:rounded-full checked:after:border-none checked:after:bg-primary checked:after:shadow-[0_3px_1px_-2px_rgba(0,0,0,0.2),_0_2px_2px_0_rgba(0,0,0,0.14),_0_1px_5px_0_rgba(0,0,0,0.12)] checked:after:transition-[background-color_0.2s,transform_0.2s] checked:after:content-["
                    "] hover:cursor-pointer focus:outline-none focus:ring-0 focus:before:scale-100 focus:before:opacity-[0.12] focus:before:shadow-[3px_-1px_0px_13px_rgba(0,0,0,0.6)] focus:before:transition-[box-shadow_0.2s,transform_0.2s] focus:after:absolute focus:after:z-[1] focus:after:block focus:after:h-5 focus:after:w-5 focus:after:rounded-full focus:after:content-["
                    "] checked:focus:border-primary checked:focus:bg-primary checked:focus:before:ml-[1.0625rem] checked:focus:before:scale-100 checked:focus:before:shadow-[3px_-1px_0px_13px_#3b71ca] checked:focus:before:transition-[box-shadow_0.2s,transform_0.2s] dark:bg-neutral-600 dark:after:bg-neutral-400 dark:checked:bg-primary dark:checked:after:bg-primary dark:focus:before:shadow-[3px_-1px_0px_13px_rgba(255,255,255,0.4)] dark:checked:focus:before:shadow-[3px_-1px_0px_13px_#3b71ca]",
                    "role": "switch",
                }
            ),
            label=_("display email"),
        )
        display_adres = forms.CharField(
            widget=forms.CheckboxInput(attrs={"class": "p-1 rounded-lg block w-full border-2"}),
            label=_("display adres"),
        )
        display_phone = forms.CharField(
            widget=forms.CheckboxInput(attrs={"class": "p-1 rounded-lg block w-full border-2"}),
            label=_("display phonenumber"),
        )
