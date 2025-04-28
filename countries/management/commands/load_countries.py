
import json
from django.core.management.base import BaseCommand
from countries.models import Country

class Command(BaseCommand):
    help = 'Load countries from GeoJSON file into database'
    
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='static/js/countries.geojson',
                          help='Path to GeoJSON file containing country data')
    
    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            with open(file_path, 'r') as file:
                geojson = json.load(file)
                
                # Process each feature (country)
                for feature in geojson['features']:
                    country_name = feature['properties']['name']
                    iso_code = ['id']
                    
                    # Create or update the country in the database
                    country, created = Country.objects.update_or_create(
                        iso_code=iso_code,
                        defaults={'name': country_name}
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created country: {country_name} ({iso_code})'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Updated country: {country_name} ({iso_code})'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON from file: {file_path}'))