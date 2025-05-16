from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from countries.models import Visit, Country
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.serializers.json import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Profile
from .forms import ProfileEditForm
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from countries.serializers import VisitSerializer

def login_view(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid username or password.')
        
        context = {
            'APPWRITE_ENDPOINT': 'https://fra.cloud.appwrite.io/v1',
            'APPWRITE_PROJECT_ID': '68125b020008f58668cb',
        }
        return render(request, 'accounts/login.html', context)
    except Exception as e:
        messages.error(request, f"Authentication error: {str(e)}")
        return render(request, 'accounts/login.html', {'error': str(e)})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    try:
        visits = Visit.objects.filter(user=request.user)
        visited_count = visits.filter(status='visited').count()
        want_to_visit_count = visits.filter(status='want_to_visit').count()
        total_countries = Country.objects.count()
        remaining_count = total_countries - (visited_count + want_to_visit_count)
        completion_percentage = (visited_count / total_countries) * 100 if total_countries > 0 else 0

        stats = [
            {'value': visited_count, 'label': 'Countries Visited', 'color': 'text-success'},
            {'value': want_to_visit_count, 'label': 'Wish List', 'color': 'text-primary'},
            {'value': remaining_count, 'label': 'Left to Explore', 'color': 'text-info'},
        ]

        # Ensure chart data is properly formatted
        visits_by_month = Visit.objects.filter(
            user=request.user,
            status='visited'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Format data for the template
        chart_labels = [visit['month'].strftime('%B %Y') for visit in visits_by_month]
        chart_data = [visit['count'] for visit in visits_by_month]

        context = {
            'visits': visits,
            'stats': stats,
            'completion_percentage': completion_percentage,
            'total_countries': total_countries,
            'visited_count': visited_count,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'profile': request.user.profile
        }
        return render(request, 'accounts/profile.html', context)
    
    except Exception as e:
        return render(request, 'accounts/profile.html', {
            'error': 'Unable to load profile data. Please try again later.',
        })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user.profile)
    
    return JsonResponse({
        'html': render_to_string('accounts/profile_edit_form.html', {
            'form': form
        }, request=request)
    })
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('countries:index')
    return redirect('countries:index')  # Fallback for GET requests

class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Visit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        visits = request.data
        created_visits = []
        
        for visit_data in visits:
            visit_data['user'] = request.user.id
            serializer = self.get_serializer(data=visit_data)
            if serializer.is_valid():
                serializer.save()
                created_visits.append(serializer.data)
        
        return Response(created_visits, status=201)