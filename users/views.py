from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from countries.models import Visit, Country

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('countries:index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('users:login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

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

        context = {
            'visits': visits,
            'stats': stats,
            'completion_percentage': completion_percentage,
            'total_countries': total_countries,
            'visited_count': visited_count,
        }
        return render(request, 'users/profile.html', context)
    
    except Exception as e:
        return render(request, 'users/profile.html', {
            'error': 'Unable to load profile data. Please try again later.',
        })

def logout_view(request):
    logout(request)
    return redirect('countries:index')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('countries:index')
    return redirect('countries:index')  # Fallback for GET requests