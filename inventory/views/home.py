from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import settings
from inventory.models import EbayItem


@login_required
def home(request):
    items = EbayItem.objects.filter(user=request.user).all()

    return render(request, "home.html",
                  {"login_url": settings.EBAY_LOGIN_URL, "items": items})
