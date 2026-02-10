import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from autotradespot.listings import models as listing_models

logger = logging.getLogger(__name__)


@api_view(["GET"])
def hello_world(request):
    return Response({"message": "Hello, world!"})


@api_view(["GET", "POST", "PUT", "DELETE"])
@authentication_classes([SessionAuthentication])
@csrf_protect
def draft(request, pk=None):
    logger.debug(f"[draft] Method: {request.method}")
    logger.debug(f"[draft] User: {request.user} (authenticated: {request.user.is_authenticated})")
    logger.debug(f"[draft] Session key: {request.session.session_key}")
    logger.debug(f"[draft] Cookies: {list(request.COOKIES.keys())}")

    if not request.user or not request.user.is_authenticated:
        logger.warning("[draft] 403: User not authenticated")
        return Response({"detail": "Authentication required"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        # Try to return an in-progress listing from session or the latest draft for this user
        listing_pk = request.session.get("listing_in_progress")
        if not listing_pk:
            listing_pk = request.GET.get("listing_pk")
        listing = None
        if listing_pk:
            listing = listing_models.Listing.objects.filter(pk=listing_pk, owner=request.user).first()
        if not listing:
            listing = (
                listing_models.Listing.objects.filter(owner=request.user, status=listing_models.Listing.Status.DRAFT)
                .order_by("-modified")
                .first()
            )

        if not listing:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        payload = {
            "listing_pk": listing.pk,
            "title": listing.title,
            "description": listing.description,
            "type": listing.type,
        }
        try:
            if hasattr(listing, "price_model_S") and listing.price_model_S:
                p = listing.price_model_S
                payload["price"] = {"pricetype": p.pricetype, "price": float(p.price)}
        except Exception:
            pass
        try:
            if hasattr(listing, "price_model_L") and listing.price_model_L:
                p = listing.price_model_L
                payload["price"] = {"pricetype": p.pricetype, "price": float(p.price), "annual_kms": p.annual_kms}
        except Exception:
            pass
        try:
            if hasattr(listing, "cardetails") and listing.cardetails:
                cd = listing.cardetails
                payload["car_details"] = {
                    "make_id": cd.make.pk if cd.make else None,
                    "model_id": cd.model.pk if cd.model else None,
                    "mileage": cd.mileage,
                    "manufacture_year": cd.manufacture_year,
                }
        except Exception:
            pass

        return Response(payload, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        listing = listing_models.Listing.objects.filter(pk=pk, owner=request.user).first()
        if listing:
            # If listing was removed, allow owner to undo deletion (restore to active)
            if listing.status == listing_models.Listing.Status.REMOVED:
                listing.set_active()
                return Response({"detail": "Listing restored"}, status=status.HTTP_200_OK)
            listing.set_under_review()
        # TODO: proper response page redirect after setting under review
        return Response({"detail": "Listing set to under review"}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        listing = listing_models.Listing.objects.filter(pk=pk, owner=request.user).first()
        if listing:
            listing.set_deleted()  # only set status to deleted
        # TODO: proper response page redirect after deletion
        return Response({"detail": "Listing deleted"}, status=status.HTTP_200_OK)

    # POST -> save/update draft
    data = request.data
    logger.debug(f"[draft POST] Received data: {data}")
    listing_pk = data.get("listing_pk")

    # Allowed simple listing fields
    listing_fields = {k: data.get(k) for k in ("title", "description", "type") if data.get(k) is not None}
    listing_fields["owner"] = request.user

    # Create or update listing
    listing, created = listing_models.Listing.objects.update_or_create(pk=listing_pk, defaults=listing_fields)

    # Persist price info depending on type
    ltype = data.get("type") or listing.type
    try:
        if ltype == "S":
            price_data = data.get("price", {})
            if price_data:
                listing_models.PricingModelBuy.objects.update_or_create(
                    listing=listing,
                    defaults={
                        "listing": listing,
                        "pricetype": price_data.get("pricetype", "F"),
                        "price": price_data.get("price", 0),
                    },
                )
        elif ltype == "L":
            price_data = data.get("price", {})
            if price_data:
                listing_models.PricingModelLease.objects.update_or_create(
                    listing=listing,
                    defaults={
                        "listing": listing,
                        "pricetype": price_data.get("pricetype", "O"),
                        "price": price_data.get("price", 0),
                        "annual_kms": price_data.get("annual_kms", 10000),
                        "lease_company": price_data.get("lease_company", ""),
                        "lease_period": price_data.get("lease_period", timezone.now().date()),
                    },
                )
    except Exception:
        # Don't fail the whole request for price save issues; return partial success
        pass

    # Car details
    car = data.get("car_details")
    if car:
        try:
            make = None
            model = None
            if car.get("make_id"):
                make = listing_models.CarMake.objects.filter(pk=car.get("make_id")).first()
            if car.get("model_id"):
                model = listing_models.CarModel.objects.filter(pk=car.get("model_id")).first()

            car_defaults = {
                "mileage": car.get("mileage", 0),
                "manufacture_year": car.get("manufacture_year", timezone.now().year),
                "transmission": car.get("transmission", listing_models.CarDetails.Transmission.MANUAL),
                "fuel_type": car.get("fuel_type", listing_models.CarDetails.FuelType.BENZINE),
                "make": make or listing_models.CarMake.objects.filter(pk=0).first(),
                "model": model or listing_models.CarModel.objects.filter(pk=0).first(),
            }
            listing_models.CarDetails.objects.update_or_create(owning_listing=listing, defaults=car_defaults)
        except Exception:
            pass

    # keep old session-based workflows compatible
    try:
        request.session["listing_in_progress"] = listing.pk
    except Exception:
        pass

    return Response({"listing_pk": listing.pk, "created": created}, status=status.HTTP_200_OK)


@api_view(["POST"])  # multipart/form-data image upload
def upload_images(request):
    if not request.user or not request.user.is_authenticated:
        return Response({"detail": "Authentication required"}, status=status.HTTP_403_FORBIDDEN)

    listing_pk = request.POST.get("listing_pk") or request.data.get("listing_pk")
    if not listing_pk:
        return Response({"detail": "listing_pk is required"}, status=status.HTTP_400_BAD_REQUEST)

    listing = get_object_or_404(listing_models.Listing, pk=listing_pk)
    if listing.owner != request.user and not request.user.is_staff:
        return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    files = request.FILES.getlist("image") or request.FILES.getlist("images")
    created = []
    for f in files:
        try:
            im = listing_models.ImageModel.objects.create(listing=listing, image=f)
            created.append({"id": im.pk, "url": im.image.url})
        except Exception:
            continue

    return Response({"images": created}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def car_makes(request):
    qs = listing_models.CarMake.objects.all().order_by("name")
    data = [{"id": m.pk, "name": m.name} for m in qs]
    return Response({"makes": data})


@api_view(["GET"])
def car_models(request):
    make = request.GET.get("make")
    if make:
        qs = listing_models.CarModel.objects.filter(make=make).order_by("name")
    else:
        qs = listing_models.CarModel.objects.all().order_by("name")
    data = [{"id": m.pk, "name": m.name, "make": m.make.pk} for m in qs]
    return Response({"models": data})


@api_view(["GET"])
def listing_types(request):
    """Returns available listing types: SALE (S) and LEASE (L)."""
    types = [{"value": choice[0], "label": str(choice[1])} for choice in listing_models.Listing.AdTypes.choices]
    return Response({"types": types})
