from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from countries.models import Country
import os
import requests
from django.conf import settings
from django.http import JsonResponse
import openai
from openai import OpenAI
@login_required
def guide(request):
    """Render the AI guide page."""
    return render(request, 'ai_guide/guide.html')

@api_view(['POST'])
@login_required
def travel_guide(request):
    """API endpoint to provide travel advice or weather information for a country."""
    country_iso = request.data.get('country_iso')
    query = request.data.get('query')

    # Validate input
    if not country_iso or not query:
        return Response({'error': 'Country ISO code and query are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the country object
    try:
        country = Country.objects.get(iso_code=country_iso)
    except Country.DoesNotExist:
        return Response({'error': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle weather-related queries
    if 'weather' in query.lower():
        api_key = os.getenv('WEATHERAPI_KEY', 'YOUR_WEATHERAPI_KEY')  # Use environment variable
        if not api_key or api_key == 'YOUR_WEATHERAPI_KEY':
            return Response({'error': 'WeatherAPI key is not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={country.name}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()
            temp_c = weather_data['current']['temp_c']
            condition = weather_data['current']['condition']['text']
            response_text = f"Current weather in {country.name}: {temp_c}°C, {condition}."
        except requests.exceptions.RequestException as e:
            return Response({'error': f"Error fetching weather data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle general travel advice queries
    else:
        api_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')  # Use environment variable
        if not api_key or api_key == 'YOUR_OPENAI_API_KEY':
            return Response({'error': 'OpenAI API key is not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            from openai import OpenAI  # Import OpenAI only if needed
            client = OpenAI(api_key=api_key)
            prompt = f"Provide travel advice for {country.name}. {query}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel guide providing helpful advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            response_text = response.choices[0].message.content.strip()
        except Exception as e:
            return Response({'error': f"Error fetching travel advice: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'response': response_text})