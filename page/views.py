from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from page.forms import WeddingMessageForm

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
