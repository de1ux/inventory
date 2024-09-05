"""
URL configuration for inventory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import settings
from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accept', views.auth.accept),
    path('register/', views.auth.register, name="register"),
    path('api/ebay/purchases/refresh', views.api.ebay.refresh_purchases, name="refresh_purchases"),
    path('api/ebay/sales/refresh', views.api.ebay.refresh_sales, name="refresh_sales"),
    path('api/ebay/token/refresh', views.api.ebay.refresh_token, name="refresh_token"),

    path('api/ebay/item/<str:pk>', views.api.item.ItemDetailView.as_view(), name="item_detail"),
    path('api/ebay/item/<str:pk>/refresh', views.api.ebay.refresh_item, name="refresh_item"),

    path('', views.home.home, name='home')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
