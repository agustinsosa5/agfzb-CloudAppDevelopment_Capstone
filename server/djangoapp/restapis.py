import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Check if api_key is provided
        if api_key:
            # Call get method with Basic authentication
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method without authentication
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
            
        response.raise_for_status()  # Agregar esta línea para manejar errores HTTP
    except requests.exceptions.RequestException as e:
        # If any error occurs
        print("Network exception occurred:", e)
        return None
    
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        # Call post method of requests library with URL, JSON payload, and other parameters
        response = requests.post(url, params=kwargs, json=json_payload)
        response.raise_for_status()  # Agregar esta línea para manejar errores HTTP
    except requests.exceptions.RequestException as e:
        # If any error occurs
        print("Network exception occurred:", e)
        return None
    
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data



def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result and "rows" in json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
        else:
            # Handle the case when "rows" key is not present in JSON
            print("Error: 'rows' key not found in JSON result")

    return results

def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


def analyze_review_sentiments(text, api_key):
    url = "URL_DE_API_WATSON_NLU_AQUI"  # Reemplaza con la URL de la API de Watson NLU
    kwargs = {
        "text": text,
        "version": "2021-03-25",  # Cambia a la versión adecuada de la API
        "features": "emotion,sentiment",
        "return_analyzed_text": True
    }
    
    response = get_request(url, api_key=api_key, **kwargs)
    
    if response:
        sentiment = response.get('sentiment', {}).get('document', {}).get('label')
        return sentiment
    else:
        return None


def get_dealer_reviews_from_cf(url, dealer_id, api_key):
    # Llamar al método get_request para obtener las reseñas del concesionario
    response = get_request(url, dealerId=dealer_id)
    
    # Convertir el resultado JSON en una lista de objetos DealerReview
    reviews_data = json.loads(response.text)
    reviews_list = []
    
    for review_data in reviews_data:
        dealer_review = DealerReview(
            dealer_id=dealer_id,
            review=review_data.get('review'),
            review_date=review_data.get('review_date')
        )
        
        # Asignar el sentimiento calculado por Watson NLU al objeto DealerReview
        dealer_review.sentiment = analyze_review_sentiments(dealer_review.review, api_key)
        
        reviews_list.append(dealer_review)
    
    return reviews_list


