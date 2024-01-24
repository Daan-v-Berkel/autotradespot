from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from portfolios.lease_finder_app.forms import MultipleFileField, StyledForm, StyledModelForm

from . import cardata
from .models import *
from .tasks import send_contact_email_task


class ListingForm(StyledModelForm):
    class Meta:
        model = Listing
        fields = (
            "title",
            "description",
            "type",
        )
        widgets = {
            "type": forms.Select(
                attrs={
                    "class": "p-1 rounded-lg block w-full border-2",
                    "hx-get": reverse_lazy("listings:getselect"),
                    "hx-target": "#priceform",
                    "hx-swap": "innerHTML",
                    "hx-trigger": "load, change",
                }
            )
        }


class ListingImageForm(StyledModelForm):
    image = MultipleFileField()

    class Meta:
        model = ImageModel
        fields = ["image"]


class CardetailForm(StyledModelForm):
    class Meta:
        model = CarDetails
        exclude = ("owning_listing", "make", "model", "variant", "options")


class OptionsSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "forms/fields/multi_checkbox.html"
    wrap_label = True


class CarOptionsForm(StyledForm):
    options = forms.ModelMultipleChoiceField(widget=OptionsSelectMultiple(attrs={}), queryset=CarOption.objects.all())


class PricingLeaseForm(StyledModelForm):
    class Meta:
        model = PricingModelLease
        exclude = (
            "listing",
            "lease_period",
        )

    lease_period = forms.DateField(
        input_formats=("%d-%m-%Y",),
        label=_("contract end date"),
        widget=forms.DateInput(attrs={"name": "lease_period", "placeholder": datetime.now().strftime("%d-%m-%Y")}),
    )
    price = forms.FloatField(label=_("Price/M"))


class PricingSaleForm(StyledModelForm):
    class Meta:
        model = PricingModelBuy
        exclude = ("listing",)


class CarMakeForm(StyledModelForm):
    make = forms.ModelChoiceField(
        queryset=CarMake.objects.all(),
        empty_label=None,
        widget=forms.Select(
            attrs={
                "class": "p-1 rounded-lg block w-full border-2",
                "size": 1,
                "hx-get": reverse_lazy("listings:getmodels"),
                "hx-target": "#id_model",
                "hx-swap": "outerHTML",
                "hx-trigger": "load, change",
            }
        ),
    )

    class Meta:
        model = CarMake
        exclude = ("makeId", "name")


class CarMakeFilter(StyledForm):
    make = forms.ChoiceField(
        choices=cardata.CarMakes.choices,
        widget=forms.Select(
            attrs={
                "class": "p-1 rounded-lg block w-full border-2",
                "size": 1,
                "hx-post": reverse_lazy("listings:filters"),
                "hx-target": "#id_model",
                "hx-swap": "outerHTML",
                "form": "filtersform",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["make"].choices = [(-1, "all")] + list(self.fields["make"].choices)


class CarModelForm(StyledModelForm):
    model = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        widget=forms.Select(
            attrs={"class": "p-1 rounded-lg block w-full border-2 disabled:hover:cursor-not-allowed", "id": "id_model"}
        ),
    )

    class Meta:
        model = CarModel
        exclude = (
            "modelId",
            "name",
            "make",
        )

    def __init__(self, *args, **kwargs):
        in_model = kwargs.get("initial", {"model": None})["model"]
        my_query = kwargs.pop("nqs")
        disabled = kwargs.pop("disabled", False)
        super().__init__(*args, **kwargs)
        self.fields["model"].queryset = my_query
        self.fields["model"].widget.attrs["disabled"] = disabled
        self.fields["model"].initial = in_model


class VariantForm(StyledForm):
    variant = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": _("extra variant details, e.g. PHEV or GT")})
    )


class CarModelFilter(StyledModelForm):
    model = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
        widget=forms.Select(
            attrs={
                "class": "p-1 rounded-lg block w-full border-2 disabled:hover:cursor-not-allowed",
                "id": "id_model",
                "form": "filtersform",
            }
        ),
    )

    class Meta:
        model = CarModel
        exclude = (
            "modelId",
            "name",
            "make",
        )

    def __init__(self, *args, **kwargs):
        my_query = kwargs.pop("nqs")
        disabled = kwargs.pop("disabled", False)
        super().__init__(*args, **kwargs)
        self.fields["model"].queryset = my_query
        self.fields["model"].widget.attrs["disabled"] = disabled


class CarDetailFilter(StyledModelForm):
    class Meta:
        model = CarDetails
        fields = (
            "fuel_type",
            "transmission",
        )
        widgets = {"fuel_type": forms.CheckboxSelectMultiple(), "transmission": forms.CheckboxSelectMultiple()}


class ContactForm(StyledForm):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 8, "cols": 40}))

    def send_email(self, recipient="admin@autotradespot.nl"):
        send_contact_email_task.delay(
            self.cleaned_data["subject"], self.cleaned_data["message"], self.cleaned_data["from_email"], [recipient]
        )


class ListingFilter(StyledForm):
    transmission = forms.MultipleChoiceField(
        choices=CarDetails.Transmission.choices, widget=forms.CheckboxSelectMultiple(), required=False
    )
    fuel_type = forms.MultipleChoiceField(
        choices=CarDetails.FuelType.choices, widget=forms.CheckboxSelectMultiple(), required=False
    )
