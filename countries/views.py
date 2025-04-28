from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Country, Visit
from .serializers import CountrySerializer, VisitSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

class MapView(LoginRequiredMixin, TemplateView):
    """Main view for the map interface"""
    template_name = 'countries/index.html'

@login_required
def profile_view(request):
    """Profile view showing user statistics"""
    visited_count = Visit.objects.filter(user=request.user, status='visited').count()
    want_to_visit_count = Visit.objects.filter(user=request.user, status='want_to_visit').count()
    total_countries = Country.objects.count()
    
    context = {
        'visited_count': visited_count,
        'want_to_visit_count': want_to_visit_count,
        'total_countries': total_countries,
        'completion_percentage': (visited_count / total_countries * 100) if total_countries > 0 else 0
    }
    
    return render(request, 'countries/profile.html', context)

# API Views
@api_view(['GET'])
def country_list(request):
    """API endpoint to get all countries"""
    countries = Country.objects.all()
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_visits(request):
    """API endpoint for getting user's visits"""
    visits = Visit.objects.filter(user=request.user)
    serializer = VisitSerializer(visits, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def create_visit(request):
    """API endpoint for creating a visit"""
    try:
        country = Country.objects.get(iso_code=request.data['iso_code'])
        visit, created = Visit.objects.get_or_create(
            user=request.user,
            country=country,
            defaults={'status': request.data['status']}
        )
        if not created:
            visit.status = request.data['status']
            visit.save()
        serializer = VisitSerializer(visit)
        return Response(serializer.data)
    except Country.DoesNotExist:
        return Response({'error': 'Country not found'}, status=404)
    
@csrf_exempt
def visits_view(request):
    if request.method == 'GET':
        return get_visits(request)
    elif request.method == 'POST':
        return create_visit(request)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@api_view(['DELETE'])
def update_delete_visit(request, iso_code):
    """API endpoint for deleting a visit"""
    try:
        visit = Visit.objects.get(user=request.user, country__iso_code=iso_code)
        visit.delete()
        return Response(status=204)
    except Visit.DoesNotExist:
        return Response({'error': 'Visit not found'}, status=404)