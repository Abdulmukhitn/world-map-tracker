from django.contrib import admin
from .models import Country, Visit

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso_code', 'visit_count')
    search_fields = ('name', 'iso_code')
    ordering = ('name',)
    list_per_page = 50

    def visit_count(self, obj):
        return obj.visit_set.count()
    visit_count.short_description = 'Total Visits'

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username', 'country__name')
    raw_id_fields = ('country',)
    date_hierarchy = 'created_at'
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs