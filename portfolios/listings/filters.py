from django import forms
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from portfolios.lease_finder_app.forms import MultipleFileField, StyledForm, StyledModelForm

from . import models


class LeaseypeFilter(StyledForm):
		type = forms.ChoiceField(choices=[(_(''), _('Any')),]+models.PricingModelLease.PriceTypeLease.choices, 
													 widget=forms.Select())


class CarMakeFilter(StyledForm):
		make = forms.ModelChoiceField(
			queryset=models.CarMake.objects.all(),
				widget=forms.Select(attrs={
														"hx-get": reverse_lazy("listings:getmodels"),
														"hx-target": "#id_model_filter",
														"hx-swap": "outerHTML",
														"hx-trigger": "change",
													 }),
				empty_label=_('Any')
		)
				

class CarModelFilter(StyledModelForm):
		model = forms.ModelChoiceField(
				queryset=None,
				empty_label=_('Any'),
				widget=forms.Select(
						attrs={
								"id": "id_model_filter",
						}
				),
		)

		class Meta:
				model = models.CarModel
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
				

class FuelTypeFilter(StyledForm):
		fuel_type = forms.ChoiceField(
			choices=[(_(''), _('Any')),]+models.CarDetails.FuelType.choices,
			widget=forms.Select(),
		)

class SalePriceFilter(StyledForm):
	from_price_sale=forms.IntegerField(min_value=0,
															 required=False,
															 label=_("min €"))
	to_price_sale=forms.IntegerField(min_value=0,
															 required=False,
															 label=_("max €"))


class LeasePriceFilter(StyledForm):
	def buildChoices(self):
		pass
	from_price_lease=forms.IntegerField(min_value=0,
															 required=False,
															 label=_("min € per month"))
	to_price_lease=forms.IntegerField(min_value=0,
															 required=False,
															 label=_("max € per month"))
	

class MileageSaleFilter(StyledForm):
	max_kms_driven = forms.IntegerField(min_value=0,
																		 required=False,
																		 label=_("max driven kilometers"))
	
class MileageLeaseFilter(StyledForm):
	ANNUALKMS = [
		(5000, '5.000'),
		(10000, '10.000'),
		(12000, '12.000'),
		(15000, '15.000'),
		(17500, '17.500'),
		(18000, '18.000'),
		(20000, '20.000'),
		(25000, '25.000'),
		(30000, '30.000'),
		(35000, '35.000'),
		(40000, '40.000+'),
	]
	min_monthly_kms = forms.IntegerField(min_value=0,
																		 required=False,
																		 label=_("min annual kilometers"),
																		 widget=forms.Select(choices=ANNUALKMS))


class LeasePeriodFilter(StyledForm):
	CONTRACTPERIODS = [
		(0,  _('any period')),
		(12, _('1 - 12 months')),
		(24, _('12 - 24 months')),
		(36, _('24 - 36 months')),
		(48, _('36 - 48 months')),
		(60, _('48 - 60 months')),
	]

	lease_period = forms.IntegerField(required=False,
																	 label=_("lease duration"),
																	 widget=forms.Select(choices=CONTRACTPERIODS))