import time

import requests
from allauth.account.decorators import verified_email_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import *
from django.db.models import Q

# from django.core.mail import BlistingHelistingerError, send_mail
from django.forms import modelformset_factory
from django.http import BadHeaderError, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from config.settings import base as settings
from portfolios.listings import forms, models, filters
from portfolios.listings.tasks import send_review_mail_task

User = get_user_model()


class HTTPResponseHXRedirect(HttpResponseRedirect):
		def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self["HX-Redirect"] = self["Location"]

		status_code = 200


def viewListing(request, pk):
		listing = models.Listing.objects.prefetch_related("imagemodel_set").get(pk=pk)

		if listing.visible_to_public():
				if request.user != listing.owner and not request.session.get(f"listing_viewed_{listing.pk}", False):
						request.session[f"listing_viewed_{listing.pk}"] = "true"
						listing.increment_views()
		else:
				if not request.user.is_staff and not request.user == listing.owner:
						raise PermissionDenied()
		return render(request, "listings/base/listing.html", context={"listing": listing})


@login_required(login_url="account_login")
@verified_email_required
def ListingCreateNew(request, save_method=None):
		if request.method == "DELETE":
				try:
						del request.session["listing_in_progress"]
				except:
						pass
				try:
						del request.session["LP_data"]
				except:
						pass
				page = render(request, "listings/create/createlisting.html")
				page.headers["HX-Refresh"] = "true"
				return page

		listing_pk = request.session.get("listing_in_progress", False)
		if request.method == "PUT" and listing_pk:
				listing = models.Listing.objects.get(pk=listing_pk)
				if save_method == "draft":
						listing.status = listing.Status.DRAFT
						listing.save()
				elif save_method == "final":
						if listing.complete_for_posting:
								listing.status = listing.Status.ACTIVE
								listing.save()
								return HTTPResponseHXRedirect(redirect_to=reverse_lazy("listings:viewlisting", args=(listing_pk,)))
		elif request.method == "PUT" and not listing_pk:
				return HttpResponse("error saving, minimum requirements not met to save the listing")
		return render(request, "listings/create/createlisting.html")


def ListingLicenceplate(request):
		if request.method == "POST":
				licenceplate = request.POST["licenceplate"].upper()
				response1 = requests.get(
						f"http://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={licenceplate}",
						headers={"X-App-Token": settings.CARDATA_API_APP_TOKEN},
				)

				response2 = requests.get(
						f"https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={licenceplate}",
						headers={"X-App-Token": settings.CARDATA_API_APP_TOKEN},
				)

				if not (response1 and response2) or not (any(response1.json()) and any(response2.json())):
						context = {
								"licence": licenceplate,
								"licence_error": _(
										f"No data has been found for licenceplate '{licenceplate}'.\nplease make sure this licenceplate you have given is correct"
								),
						}
						return render(request, "listings/create/createlistingLP.html", context)

				data_combined = response1.json()[0] | response2.json()[0]
				relevant_data = {"licence": licenceplate}
				# only store relevant data in session
				for name, api_name in settings.RELEVANT_CARDATA_FIELDS.items():
						relevant_data[name] = data_combined.get(api_name)

				request.session["LP_data"] = relevant_data
				return redirect("listings:createlistingtype")
		else:
				context = {"licence": request.session.get("LP_data", {"licence": ""})["licence"]}
				return render(request, "listings/create/createlistingLP.html", context)


def ListingType(request):
		if request.method == "POST":
				form = forms.ListingForm(request.POST)
				type = request.POST.get("type")
				if type == "S":
						priceform = forms.PricingSaleForm(request.POST)
				elif type == "L":
						priceform = forms.PricingLeaseForm(request.POST)
				print(f"form_errors: {priceform.errors}")
				if form.is_valid() and priceform.is_valid():
						listing, created = models.Listing.objects.update_or_create(
								pk=request.session.get("listing_in_progress"), defaults=form.cleaned_data | {"owner": request.user}
						)
						if type == "S":
								p, c = models.PricingModelBuy.objects.update_or_create(
										listing=listing, defaults=priceform.cleaned_data | {"listing": listing}
								)
						elif type == "L":
								p, c = models.PricingModelLease.objects.update_or_create(
										listing=listing, defaults=priceform.cleaned_data | {"listing": listing}
								)
						request.session["listing_in_progress"] = listing.pk
						return redirect("listings:createlistingmake")
				else:
						return render(
								request, "listings/create/createlistingtype.html", context={"form1": form, "priceform": priceform}
						)

		if "listing_in_progress" in request.session:
				current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
				form = forms.ListingForm(instance=current_listing)
		elif "LP_data" in request.session:
				substitute_title = f"{request.session['LP_data']['make']} {request.session['LP_data']['model']}"
				form = forms.ListingForm(initial={"title": substitute_title})
		else:
				form = forms.ListingForm()
		priceform = forms.PricingLeaseForm
		return render(request, "listings/create/createlistingtype.html", context={"form1": form, "priceform": priceform})


def ListingMake(request):
		if request.method == "POST":
				make_form = forms.CarMakeForm(request.POST)
				model_form = forms.CarModelForm(
						request.POST, nqs=models.CarModel.objects.filter(make=request.POST.get("make", 0))
				)
				variant_form = forms.VariantForm(request.POST)
				if make_form.is_valid() and model_form.is_valid() and variant_form.is_valid():
						d = request.session.get("LP_data", {})
						d["makeId"] = request.POST.get("make", 0)
						d["modelId"] = request.POST.get("model", 0)
						d["variant"] = variant_form.cleaned_data["variant"]
						request.session["LP_data"] = d
						return redirect("listings:createlistingdetails")
		else:
				make = request.GET.get("make", 0)
				nqs = models.CarModel.objects.filter(make=make)
				d = request.session.get("LP_data", {})
				if d:
						listing_make_qs = models.CarMake.objects.filter(name__iexact=d["make"])
						listing_make = listing_make_qs[0] if listing_make_qs else ""
						listing_model_qs = models.CarModel.objects.filter(Q(name__iexact=d["model"]), Q(make=listing_make))
						listing_model = listing_model_qs if listing_model_qs else ""
						make_form = forms.CarMakeForm(initial={"make": listing_make})
				else:
						make_form = forms.CarMakeForm()
				model_form = forms.CarModelForm(nqs=nqs, disabled=True)
				# model_form.data = {"model":listing_model}
				variant_form = forms.VariantForm()
		return render(
				request,
				"listings/create/createlistingmake.html",
				context={"make_form": make_form, "model_form": model_form, "variant_form": variant_form},
		)


def ListingDetails(request):
		if request.method == "POST":
				details_form = forms.CardetailForm(request.POST)
				caroptions_form = forms.CarOptionsForm(request.POST)
				if details_form.is_valid() and caroptions_form.is_valid():
						current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
						make = models.CarMake.objects.get(pk=request.session["LP_data"]["makeId"])
						model = models.CarModel.objects.get(pk=request.session["LP_data"]["modelId"])
						variant = request.session["LP_data"]["variant"]
						options = caroptions_form.cleaned_data["options"]
						details, created = models.CarDetails.objects.update_or_create(
								owning_listing=current_listing,
								defaults=details_form.cleaned_data
								| {"owning_listing": current_listing, "make": make, "model": model, "variant": variant},
						)
						print(f"detail_options:{options}")
						details.options.set(options)
						return redirect("listings:uploadlistingimages")
				else:
						return render(
								request,
								"listings/create/createlistingdetails.html",
								context={"form4": details_form, "caroptions_form": caroptions_form},
						)

		print(f'lp_data in cardetails: {request.session.get("LP_data")}')
		form4 = forms.CardetailForm(initial=request.session.get("LP_data") or {})
		caroptions_form = forms.CarOptionsForm()
		if "listing_in_progress" in request.session:
				current_listing = models.Listing.objects.get(pk=request.session.get("listing_in_progress"))
				try:
						car_details = current_listing.cardetails
						car_options = car_details.options
						form4 = forms.CardetailForm(instance=car_details)
						caroptions_form = forms.CarOptionsForm(instance=car_options)
				except:
						pass
		return render(
				request,
				"listings/create/createlistingdetails.html",
				context={"form4": form4, "caroptions_form": caroptions_form},
		)


def ListingImages(request, image_pk=None):
		imageform = forms.ListingImageForm()
		listing = models.Listing.objects.filter(pk=request.session.get("listing_in_progress", -1)).first()

		if request.method == "POST":
				imageform = forms.ListingImageForm(request.POST, request.FILES)
				if imageform.is_valid():
						images = request.FILES.getlist("image")
						for i in images:
								models.ImageModel.objects.create(listing=listing, image=i)
						return redirect("listings:listingpreview", listing_pk=listing.pk)

		elif request.method == "DELETE":
				print(f"trying to delete an image: {models.ImageModel.objects.get(pk=image_pk)}")
				models.ImageModel.objects.get(pk=image_pk).delete()

		return render(
				request, "listings/create/uploadlistingimages.html", context={"imageform": imageform, "listing": listing}
		)


def PreviewListing(request, listing_pk=-1):
		if listing_pk == -1:
				listing_pk = int(request.session.get("listing_in_progress") or 0)

		if int(listing_pk) < 1:
				listing = None
		else:
				listing = models.Listing.objects.get(pk=listing_pk)
		return render(request, "listings/create/listingpreview.html", context={"listing": listing})


def GetSelect(request):
		# TODO: rename
		type = request.GET.get("type")
		print(f"pricingtype: {type}")
		if type == "S":
				form1 = forms.PricingSaleForm()
		elif type == "L":
				form1 = forms.PricingLeaseForm()
		else:
				return HttpResponse()
		return render(request, "listings/partials/pricingform.html", context={"form1": form1})


def ModifyListing(request, pk, action="modify"):
		listing = models.Listing.objects.get(pk=pk)

		if request.method == "POST" and action == "delete":
				listing.set_deleted()
				return redirect("users:detail")

		elif request.method == "PUT":
				if action == "activate":
						listing.set_under_review()
						page = render(
								request,
								"listings/base/listing.html",
								context={"listing": listing, "favourites_cnt": len(listing.favourites_list.all())},
						)
						page.headers["HX-Refresh"] = "true"
						return page

				elif action == "modify":
						request.session["listing_in_progress"] = listing.pk
						return HTTPResponseHXRedirect(reverse_lazy("listings:createlistingnew"))


def contactView(request, pk=None):
		listing = get_object_or_404(models.Listing, pk=pk)
		if request.method == "GET":
				umail = request.user.email if request.user.is_authenticated else ""
				subject = _("Interest in your listing")
				message = _(
						f"Hi there,\n\nI am interested in your listing on Auto Tradespot!\nPlease contact me by replying to this email.\n\nWith regards, {request.user.name}"
				)
				form = forms.ContactForm(initial={"from_email": umail, "subject": subject, "message": message})
		else:
				form = forms.ContactForm(request.POST)
				if form.is_valid():
						try:
								form.send_email(recipient=listing.owner.email)
						except BadHeaderError:
								return HttpResponse("Invalid header found.")
						return HttpResponse(_("Thank you for your interest, the provider of this listing will contact you soon!"))
		return render(request, "listings/contact/contact_form.html", {"form": form, "listing_pk": listing.pk})


def getModels(request, filter='filter'):
		make = request.GET.get("make", 0)
		if make:
			nqs=models.CarModel.objects.filter(make=make)
		else:
			nqs = models.CarMake.objects.all()
		if filter == 'filter':
			form = filters.CarModelFilter(nqs=nqs)
		else:
			form = forms.CarModelForm(nqs=nqs)
		return HttpResponse(form)


def searchListing(request):
		lm = models.Listing
		base_qs = models.Listing.objects.filter(status__exact=lm.Status.ACTIVE, type__exact='S')
		leasetypefilter = filters.LeaseypeFilter()
		makefilter = filters.CarMakeFilter()
		modelfilter = filters.CarModelFilter(nqs=models.CarModel.objects.all())
		leasepricefilter = filters.LeasePriceFilter()
		salepricefilter = filters.SalePriceFilter()
		mileagesalefilter = filters.MileageSaleFilter()
		mileageleasefilter = filters.MileageLeaseFilter()
		leaseperiodfilter = filters.LeasePeriodFilter()
		context = {
						'leasetypefilter': leasetypefilter,
						'makefilter': makefilter,
						'modelfilter': modelfilter,
						'leasepricefilter': leasepricefilter,
						'salepricefilter': salepricefilter,
						'mileagesalefilter': mileagesalefilter,
						'mileageleasefilter': mileageleasefilter,
						'leaseperiodfilter': leaseperiodfilter,
		}
		return render(request, "listings/search/searcher.html", context=context)

@require_POST
def FilterListings(request):
		print(request.POST.dict())
		qs = models.Listing.objects.search(searchdict=request.POST.dict())
		print(qs)

		return render(request, "listings/search/listing_section_searchresults.html", context={'listings':qs})