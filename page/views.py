from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from page.forms import WeddingMediaUploadForm, WeddingMessageForm
from page.models import WeddingPhoto

# Create your views here.


def home(request):
    form = WeddingMessageForm()
    return render(request, "home.html", {"contact_form": form})


def send_message(request):
    if request.method == "POST":
        form = WeddingMessageForm(request.POST)
        if form.is_valid():
            form.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True})
            return redirect(reverse("home") + f"#contact-form")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "errors": form.errors.get_json_data()},
                status=400,
            )
        return render(
            request, "home.html", {"contact_form": form}, status=400
        )
    return redirect(reverse("home") + f"#contact-form")


def upload_photos(request):
    if request.method != "POST":
        return redirect(reverse("home") + "#share-photo")

    form = WeddingMediaUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "errors": form.errors.get_json_data()},
                status=400,
            )
        return render(
            request,
            "home.html",
            {
                "contact_form": WeddingMessageForm(),
                "media_upload_errors": form.errors,
            },
            status=400,
        )

    with transaction.atomic():
        media_items = [
            WeddingPhoto.objects.create(file=media_file)
            for media_file in form.cleaned_data["media_files"]
        ]

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "uploaded_count": len(media_items)})
    return redirect(reverse("home") + "#share-photo")
