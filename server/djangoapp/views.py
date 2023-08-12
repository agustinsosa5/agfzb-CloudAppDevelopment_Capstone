from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarMake, CarModel
from .restapis import get_request, get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required

import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def my_view(request):
    return render(request, 'static_template.html')

# Create an `about` view to render a static about page
# def about(request):
def about_us(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact_us(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('psw')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')  # Cambia 'index' por el nombre de la vista a la que quieres redireccionar después del inicio de sesión
        else:
            messages.error(request, 'Invalid username or password.')  # Agrega un mensaje de error en caso de inicio de sesión fallido                
    # Si la solicitud es GET, muestra el formulario de inicio de sesión
    return render(request, 'djangoapp/index.html')


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/d4b20026-84fb-49cb-a3e2-670b5ccdb663/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/d4b20026-84fb-49cb-a3e2-670b5ccdb663/dealership-package/get-review"
        dealer_review = get_dealer_reviews_from_cf(url, dealer_id, api_key)
        review = ' '.join([dealer.review for dealer in dealer_review])
        # Return a list of dealer short name
        return HttpResponse(review)


def add_review(request, dealer_id):
    if request.method == "POST":
        url = "URL_DE_API_AQUI"  # Asigna la URL de la API para publicar reseñas
        
        # Crea el diccionario de la reseña
        review = {
            "time": datetime.utcnow().isoformat(),
            "dealership": dealer_id,
            "review": request.POST.get('review')  # Obtiene la reseña del formulario o de donde sea necesario
        }
        
        # Crea el diccionario json_payload con la reseña
        json_payload = {
            "review": review
        }
        
        # Llama al método post_request para realizar la solicitud POST
        response = post_request(url, json_payload, dealerId=dealer_id)
        
        if response:
            # Puedes imprimir la respuesta en la consola o incluirla en la respuesta HTTP
            print("Post Response:", response)
            return HttpResponse("Review added successfully.")
        else:
            return HttpResponse("Failed to add review.")


