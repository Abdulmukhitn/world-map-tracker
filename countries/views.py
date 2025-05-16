from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Country, Visit, TravelPlan, TravelJournal, Achievement
from django.db.models import Count, Sum, Avg
from django.db.models.functions import ExtractMonth
from .serializers import CountrySerializer, VisitSerializer, TravelPlanSerializer, TravelTipSerializer, TravelJournalSerializer, TravelGroupSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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

@login_required
def travel_stats(request):
    """View for displaying user's travel statistics"""
    stats = {
        'total_countries': Visit.objects.filter(
            user=request.user, 
            status='visited'
        ).count(),
        
        'continents_visited': Visit.objects.filter(
            user=request.user, 
            status='visited'
        ).values('country__continent').distinct().count(),
        
        'top_regions': Visit.objects.filter(
            user=request.user, 
            status='visited'
        ).values('country__region').annotate(
            count=Count('id')
        ).order_by('-count')[:5],
        
        'recent_visits': Visit.objects.filter(
            user=request.user, 
            status='visited'
        ).order_by('-created_at')[:5],
        
        'planned_trips': TravelPlan.objects.filter(
            user=request.user
        ).order_by('planned_date')[:5]
    }
    
    return render(request, 'countries/travel_stats.html', {'stats': stats})

@login_required
def achievement_list(request):
    visited_countries = Visit.objects.filter(
        user=request.user, 
        status='visited'
    )
    
    user_stats = {
        'countries_visited': visited_countries.count(),
        'continents_visited': visited_countries.values(
            'country__continent'
        ).distinct().count(),
    }

    achievements = {
        'explorer': {
            'name': 'World Explorer',
            'levels': [
                {'count': 5, 'title': 'Novice Explorer', 'icon': 'fa-walking'},
                {'count': 10, 'title': 'Adventurer', 'icon': 'fa-hiking'},
                {'count': 25, 'title': 'Globe Trotter', 'icon': 'fa-plane'},
                {'count': 50, 'title': 'World Citizen', 'icon': 'fa-globe-americas'},
                {'count': 100, 'title': 'Master Explorer', 'icon': 'fa-earth-americas'}
            ]
        },
        'continent': {
            'name': 'Continent Collector',
            'levels': [
                {'count': 1, 'title': 'Continental Starter', 'icon': 'fa-flag'},
                {'count': 3, 'title': 'Region Explorer', 'icon': 'fa-map-location'},
                {'count': 5, 'title': 'World Wanderer', 'icon': 'fa-map-marked-alt'},
                {'count': 7, 'title': 'Global Navigator', 'icon': 'fa-compass'}
            ]
        }
    }

    return render(request, 'countries/achievements.html', {
        'achievements': achievements,
        'stats': user_stats
    })

# API Views
@api_view(['GET'])
def country_list(request):
    """API endpoint to get all countries"""
    countries = Country.objects.all()
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@login_required
def visits_view(request):
    """API endpoint to list and create visits"""
    if request.method == 'GET':
        visits = Visit.objects.filter(user=request.user)
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
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

@api_view(['DELETE', 'PUT'])
@login_required
def visit_detail(request, iso_code):
    """API endpoint to update or delete a visit"""
    try:
        visit = Visit.objects.get(
            user=request.user,
            country__iso_code=iso_code
        )
        
        if request.method == 'DELETE':
            visit.delete()
            return Response(status=204)
            
        elif request.method == 'PUT':
            visit.status = request.data.get('status', visit.status)
            visit.save()
            serializer = VisitSerializer(visit)
            return Response(serializer.data)
            
    except Visit.DoesNotExist:
        return Response({'error': 'Visit not found'}, status=404)

class TravelPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TravelPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TravelPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TravelJournalViewSet(viewsets.ModelViewSet):
    serializer_class = TravelJournalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TravelJournal.objects.filter(user=self.request.user)

class TravelGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TravelGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        group.members.add(request.user)
        return Response({'status': 'joined group'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = self.get_object()
        group.members.remove(request.user)
        return Response({'status': 'left group'})

class TravelTipViewSet(viewsets.ModelViewSet):
    serializer_class = TravelTipSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        tip = self.get_object()
        tip.upvotes.add(request.user)
        return Response({'status': 'tip upvoted'})



@api_view(['GET'])
@login_required
def travel_stats_api(request):
    visited_countries = Visit.objects.filter(
        user=request.user,
        status='visited'
    )
    
    stats = {
        'top_regions': list(
            visited_countries.values('country__region')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        ),
        'visits_by_month': list(
            visited_countries
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
    }
    return Response(stats)