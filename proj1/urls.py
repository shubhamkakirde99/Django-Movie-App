"""proj1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from vdoApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.loginPage),
    path("login/", views.login),        # login page
    path("logout/", views.logout),
    path("movieList/", views.movieList),    # list of movies page
    path("movie/<str:key>/", views.movie),  # specific movie page
    path("delete/<str:key>/", views.deleteMovie),   # if admin deletes
    path("editTitle/<str:key>/", views.editTitle),  # if admin edits
    path("addVideo/", views.addVideo),              # if admin adds video
    path("comment/<str:key>/", views.addComment),   # if user comments
    path("apiView/movieList/", views.apiMovies),    # api view for movie list
    path("apiView/link/<str:key>/", views.apiLink),      # api view for link
]
