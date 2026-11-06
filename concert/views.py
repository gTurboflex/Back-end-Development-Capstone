from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req
from django.conf import settings


# Create your views here.

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(**form.cleaned_data)
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": form})


def index(request):
    return render(request, "index.html")


def songs(request):
    # songs = {"songs":[]}
    # return render(request, "songs.html", {"songs": [insert list here]})
    return service_page(request, "songs.html", "songs", settings.SONGS_SERVICE + "/song")


def photos(request):
    # photos = []
    # return render(request, "photos.html", {"photos": photos})
    return service_page(request, "photos.html", "photos", settings.PICTURES_SERVICE + "/picture")


def service_page(request, template, key, url):
    try:
        response = req.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Expected a resource list")
        return render(request, template, {key: data})
    except (req.RequestException, ValueError):
        return render(request, template, {key: [], "service_error": "Service temporarily unavailable."}, status=503)

def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse("index"))
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def concerts(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    statuses = dict(ConcertAttending.objects.filter(user=request.user).values_list("concert_id", "attending"))
    items = [{"concert": concert, "status": statuses.get(concert.id, "-")}
             for concert in Concert.objects.order_by("date", "id")]
    return render(request, "concerts.html", {"concerts": items})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = get_object_or_404(Concert, pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            get_object_or_404(Concert, pk=concert_id)
            if attendee_status not in ConcertAttending.AttendingChoices.values:
                return HttpResponse("Invalid attendance status", status=400)
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
