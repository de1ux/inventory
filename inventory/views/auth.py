import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
import settings
from inventory.forms import RegisterForm

@login_required
def accept(request):
    code = request.GET.get('code')

    data = f"grant_type=authorization_code&code={code}&redirect_uri={settings.EBAY_REDIRECT_URI}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {settings.EBAY_CLIENT_SECRET}"
    }

    response = requests.post("https://api.ebay.com/identity/v1/oauth2/token", headers=headers, data=data)
    response.raise_for_status()

    user = request.user
    user.ebay_refresh_token = response.json()['refresh_token']
    user.ebay_token = response.json()['access_token']
    user.save()

    return redirect("/")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect("/")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})
