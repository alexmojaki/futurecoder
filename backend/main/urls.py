"""book URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from main.text import chapters
from main.views import api_view, FrontendAppView, HomePageView

home_view = HomePageView.as_view()
urlpatterns = [
    path('api/<method_name>/', api_view),
    path('home/', home_view),
    path('', home_view),
    path('course/', ensure_csrf_cookie(FrontendAppView.as_view())),
    path('toc/', TemplateView.as_view(template_name="toc.html", extra_context=dict(chapters=chapters))),
]
