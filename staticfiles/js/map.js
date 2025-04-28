// Global variables
let mapInstance = null;
let countriesGeoJSON = null;
let visits = [];

document.addEventListener('DOMContentLoaded', function() {
    // Check if map container exists
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found');
        return;
    }

    // If map is already initialized, remove it
    if (mapInstance) {
        mapInstance.remove();
    }

    // Initialize the map
    mapInstance = L.map('map', {
        minZoom: 2,
        maxZoom: 5,
        worldCopyJump: true,
        center: [20, 0],
        zoom: 2
    });

    // Add tile layer
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapInstance);

    // Add legend
    const legend = L.control({position: 'bottomright'});
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = `
            <i style="background: #ff0000"></i> Visited<br>
            <i style="background: #00ff00"></i> Want to Visit<br>
            <i style="background: #3388ff"></i> Not Visited<br>
        `;
        div.style.padding = '6px 8px';
        div.style.background = 'rgba(255,255,255,0.8)';
        div.style.borderRadius = '5px';
        div.style.lineHeight = '18px';
        div.style.color = '#555';

        div.querySelectorAll('i').forEach(el => {
            el.style.width = '18px';
            el.style.height = '18px';
            el.style.float = 'left';
            el.style.marginRight = '8px';
            el.style.opacity = '0.7';
        });
        return div;
    };
    legend.addTo(mapInstance);

    // Add info control
    const info = L.control();
    info.onAdd = function() {
        this._div = L.DomUtil.create('div', 'info');
        this._div.style.padding = '6px 8px';
        this._div.style.background = 'rgba(255,255,255,0.8)';
        this._div.style.borderRadius = '5px';
        this.update();
        return this._div;
    };
    
    info.update = function(props) {
        // Fixed ISO code extraction with better fallback handling
        const isoCode = props ? getIsoCode(props) : '';
        this._div.innerHTML = '<h4>Country Info</h4>' + (props ?
            '<b>' + props.name + '</b><br />ISO: ' + isoCode :
            'Hover over a country');
    };
    info.addTo(mapInstance);

    // Helper function to extract ISO code consistently
    function getIsoCode(feature) {
        if (!feature) return '';
        
        // If feature is a string or direct ID, return it
        if (typeof feature === 'string') return feature;
        
        // Check if we're getting the full feature or just properties
        const props = feature.properties || feature;
        
        // Try all possible ISO code variations in order of preference
        return props.ISO_A2 || // Standard uppercase
               props.iso_a2 || // Standard lowercase
               props.ISO2 ||   // Alternative format
               props.iso2 ||   // Alternative lowercase
               (props.iso && props.iso.toUpperCase()) || // ISO property
               props.ISO_A3 || // 3-letter code uppercase
               props.iso_a3 || // 3-letter code lowercase
               '';
    }

    // Fetch countries and visits
    const visitedCountriesList = document.getElementById('visited-countries');
    const wantToVisitCountriesList = document.getElementById('want-to-visit-countries');

    // Function to get CSRF token
    function getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    // Fetch all GeoJSON data first
    fetch('/static/js/countries.geojson')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch GeoJSON');
            return response.json();
        })
        .then(geojson => {
            console.log("GeoJSON loaded successfully");
            // Validate the GeoJSON data
            if (!geojson || !geojson.features || !Array.isArray(geojson.features)) {
                throw new Error('Invalid GeoJSON data structure');
            }
            
            // Log a sample feature to check the structure
            if (geojson.features.length > 0) {
                console.log("Sample country properties:", geojson.features[0].properties);
            }
            
            countriesGeoJSON = geojson;
            
            // Then fetch user visits
            return fetch('/api/visits/');
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch visits');
            return response.json();
        })
        .then(data => {
            console.log("User visits loaded:", data);
            visits = data;
            updateMap();
            updateLists();
        })
        .catch(error => {
            console.error('Error loading visits:', error);
            showNotification('Failed to load visits. Please refresh the page.', 'warning');
            // Still try to load the map even if visits can't be fetched
            if (countriesGeoJSON) {
                updateMap();
            }
        });

    function updateMap() {
        if (!countriesGeoJSON) {
            console.error("No GeoJSON data available");
            return;
        }
        
        console.log("Updating map with visits:", visits);
        
        // Clear existing GeoJSON layers
        mapInstance.eachLayer(layer => {
            if (layer instanceof L.GeoJSON) {
                mapInstance.removeLayer(layer);
            }
        });

        // Create arrays of ISO codes for easy lookup
        const visitedIsoCodes = visits
            .filter(v => v.status === 'visited')
            .map(v => v.country.iso_code);
            
        const wantToVisitIsoCodes = visits
            .filter(v => v.status === 'want_to_visit')
            .map(v => v.country.iso_code);
            
        console.log("Visited countries:", visitedIsoCodes);
        console.log("Want to visit countries:", wantToVisitIsoCodes);

        L.geoJSON(countriesGeoJSON, {
            style: function(feature) {
                // Get ISO code from the feature properties
                const isoCode = getIsoCode(feature.id);
                
                let fillColor = '#3388ff'; // Default blue - Not visited
                
                if (visitedIsoCodes.includes(isoCode)) {
                    fillColor = '#ff0000'; // Red - Visited
                } else if (wantToVisitIsoCodes.includes(isoCode)) {
                    fillColor = '#00ff00'; // Green - Want to visit
                }
                
                return {
                    fillColor: fillColor,
                    weight: 1,
                    opacity: 1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity: 0.7
                };
            },
            onEachFeature: function(feature, layer) {
                // Get country details from properties with improved ISO extraction
                const countryName = feature.properties.name;
                const isoCode = getIsoCode(feature.id);
                
                if (!isoCode) {
                    console.warn(`No ISO code found for country: ${countryName}`, feature);
                }
                
                layer.on({
                    mouseover: function(e) {
                        const layer = e.target;
                        layer.setStyle({
                            weight: 2,
                            color: '#666',
                            dashArray: '',
                            fillOpacity: 0.9
                        });
                        info.update(feature.properties);
                    },
                    mouseout: function(e) {
                        const layer = e.target;
                        layer.setStyle({
                            weight: 1,
                            color: 'white',
                            dashArray: '3',
                            fillOpacity: 0.7
                        });
                        info.update();
                    },
                    click: function(e) {
                        if (!isoCode) {
                            console.error('Cannot mark country without ISO code:', countryName);
                            showNotification('Error: This country does not have a valid ISO code', 'danger');
                            return;
                        }
                        
                        // Check current status
                        const isVisited = visitedIsoCodes.includes(isoCode);
                        const isWantToVisit = wantToVisitIsoCodes.includes(isoCode);
                        let statusText = '';
                        
                        if (isVisited) {
                            statusText = '<div class="alert alert-success">Already marked as Visited</div>';
                        } else if (isWantToVisit) {
                            statusText = '<div class="alert alert-info">Already marked as Want to Visit</div>';
                        }
                        
                        const popup = L.popup({
                            className: 'country-popup',
                            maxWidth: 300
                        })
                        .setLatLng(e.latlng)
                        .setContent(`
                            <div class="country-modal">
                                <h5>${countryName}</h5>
                                <p class="text-muted">ISO Code: ${isoCode}</p>
                                ${statusText}
                                <div class="d-grid gap-2">
                                    <button class="btn btn-success mb-2" onclick="markCountry('${isoCode}', 'visited')">
                                        <i class="fas fa-check-circle"></i> Mark as Visited
                                    </button>
                                    <button class="btn btn-primary mb-2" onclick="markCountry('${isoCode}', 'want_to_visit')">
                                        <i class="fas fa-plane"></i> Want to Visit
                                    </button>
                                    ${(isVisited || isWantToVisit) ? 
                                    `<button class="btn btn-outline-danger" onclick="removeCountry('${isoCode}')">
                                        <i class="fas fa-trash"></i> Remove
                                    </button>` : ''}
                                </div>
                            </div>
                        `)
                        .openOn(mapInstance);
                    }
                });
            }
        }).addTo(mapInstance);
    }

    function updateLists() {
        if (!visitedCountriesList || !wantToVisitCountriesList) {
            console.warn("Country lists elements not found in the DOM");
            return;
        }
        
        // Clear existing lists
        visitedCountriesList.innerHTML = '';
        wantToVisitCountriesList.innerHTML = '';
        
        // Sort visits by country name
        const sortedVisits = [...visits].sort((a, b) => 
            a.country.name.localeCompare(b.country.name)
        );
        
        // Filter and populate lists
        const visitedCountries = sortedVisits.filter(v => v.status === 'visited');
        const wantToVisitCountries = sortedVisits.filter(v => v.status === 'want_to_visit');
        
        if (visitedCountries.length === 0) {
            visitedCountriesList.innerHTML = '<li class="list-group-item text-center text-muted">No countries marked as visited yet</li>';
        } else {
            visitedCountries.forEach(visit => addCountryToList(visit, visitedCountriesList));
        }
        
        if (wantToVisitCountries.length === 0) {
            wantToVisitCountriesList.innerHTML = '<li class="list-group-item text-center text-muted">No countries in your travel wishlist yet</li>';
        } else {
            wantToVisitCountries.forEach(visit => addCountryToList(visit, wantToVisitCountriesList));
        }
    }
    
    function addCountryToList(visit, listElement) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Add flag if available
        if (visit.country.iso_code && visit.country.iso_code.length === 2) {
            const flagEmoji = getFlagEmoji(visit.country.iso_code);
            li.innerHTML = `<span>${flagEmoji} ${visit.country.name}</span>`;
        } else {
            li.innerHTML = `<span>${visit.country.name}</span>`;
        }
        
        // Add action buttons
        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group btn-group-sm';
        
        // Add appropriate action button based on current list
        if (visit.status === 'visited') {
            // In visited list, add "move to want to visit" button
            const moveBtn = document.createElement('button');
            moveBtn.className = 'btn btn-outline-primary';
            moveBtn.innerHTML = '<i class="fas fa-plane"></i>';
            moveBtn.title = 'Move to Want to Visit';
            moveBtn.onclick = () => markCountry(visit.country.iso_code, 'want_to_visit');
            btnGroup.appendChild(moveBtn);
        } else {
            // In want to visit list, add "mark as visited" button
            const visitedBtn = document.createElement('button');
            visitedBtn.className = 'btn btn-outline-success';
            visitedBtn.innerHTML = '<i class="fas fa-check"></i>';
            visitedBtn.title = 'Mark as Visited';
            visitedBtn.onclick = () => markCountry(visit.country.iso_code, 'visited');
            btnGroup.appendChild(visitedBtn);
        }
        
        // Add remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-outline-danger ms-1';
        removeBtn.innerHTML = '<i class="fas fa-trash"></i>';
        removeBtn.title = 'Remove';
        removeBtn.onclick = () => removeCountry(visit.country.iso_code);
        btnGroup.appendChild(removeBtn);
        
        li.appendChild(btnGroup);
        listElement.appendChild(li);
    }

    // Replace the existing createVisit function
    async function createVisit(isoCode, status) {
        console.log(`Creating visit for ${isoCode} with status ${status}`);
        
        // Validate inputs
        if (!isoCode || !status) {
            showNotification('Error: Invalid parameters', 'danger');
            return;
        }

        try {
            const response = await fetch('/api/visits/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ 
                    iso_code: isoCode, 
                    status: status 
                }),
            });

            

            const data = await response.json();
            console.log('Visit created successfully:', data);
            
            // Update local data
            visits.push(data);
            
            // Update UI
            mapInstance.closePopup();
            showNotification(`Country marked as ${status === 'visited' ? 'visited' : 'want to visit'}`);
            
            // Refresh map and lists
            updateMap();
            updateLists();

        } catch (error) {
            console.error('Error creating visit:', error);
            showNotification(`Failed to mark country: ${error.message}`, 'danger');
        }
    }

    function updateVisit(isoCode, status) {
        console.log(`Updating visit for ${isoCode} to ${status}`);
        
        // Check that we have a valid ISO code
        if (!isoCode) {
            showNotification('Error: Invalid country code', 'danger');
            return;
        }
        
        fetch(`/countries/api/visits/${isoCode}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ status: status }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to update visit: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Visit updated successfully:', data);
            // Find and update the visit in our local data
            const index = visits.findIndex(v => v.country.iso_code === isoCode);
            if (index !== -1) {
                visits[index] = data;
            }
            mapInstance.closePopup();
            showNotification(`Country updated to ${status === 'visited' ? 'visited' : 'want to visit'}`);
            updateMap();
            updateLists();
        })
        .catch(error => {
            console.error('Error updating visit:', error);
            showNotification('Failed to update country. Please try again.', 'danger');
        });
    }

    function removeCountry(isoCode) {
        console.log(`Removing country ${isoCode}`);
        
        // Check that we have a valid ISO code
        if (!isoCode) {
            showNotification('Error: Invalid country code', 'danger');
            return;
        }
        
        fetch(`/countries/api/visits/${isoCode}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to delete visit: ${response.status} ${response.statusText}`);
            }
            // Filter out the removed country from our local data
            visits = visits.filter(v => v.country.iso_code !== isoCode);
            mapInstance.closePopup();
            showNotification('Country removed from your lists');
            updateMap();
            updateLists();
        })
        .catch(error => {
            console.error('Error removing country:', error);
            showNotification('Failed to remove country. Please try again.', 'danger');
        });
    }

    // Helper function to convert ISO code to flag emoji
    function getFlagEmoji(isoCode) {
        if (!isoCode || isoCode.length !== 2) return '';
        return isoCode
            .toUpperCase()
            .split('')
            .map(char => String.fromCodePoint(char.charCodeAt(0) + 127397))
            .join('');
    }

    // Function to show notifications
    function showNotification(message, type = 'success') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('map-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'map-notification';
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.maxWidth = '300px';
            notification.style.zIndex = '9999';
            document.body.appendChild(notification);
        }
        
        // Set notification content
        notification.className = `alert alert-${type} shadow`;
        notification.textContent = message;
        notification.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                notification.style.display = 'none';
                notification.style.opacity = '1';
            }, 500);
        }, 3000);
    }

    // Make markCountry function available globally
    window.markCountry = function(isoCode, status) {
        if (!isoCode) {
            console.error('Invalid ISO code');
            showNotification('Error: Invalid country code', 'danger');
            return;
        }
        
        // Check if country is already in list with this status
        const existingVisit = visits.find(v => v.country.iso_code === isoCode);
        
        if (existingVisit) {
            if (existingVisit.status === status) {
                showNotification(`Country is already marked as ${status === 'visited' ? 'visited' : 'want to visit'}`);
            } else {
                updateVisit(isoCode, status);
            }
        } else {
            createVisit(isoCode, status);
        }
    };

    // Make removeCountry function available globally
    window.removeCountry = function(isoCode) {
        removeCountry(isoCode);
    };

    // Add search functionality
    const searchInput = document.getElementById('country-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            if (!countriesGeoJSON || !countriesGeoJSON.features) return;
            
            const results = countriesGeoJSON.features
                .filter(feature => {
                    const countryName = feature.properties.name || '';
                    return countryName.toLowerCase().includes(searchTerm);
                })
                .slice(0, 5); // Limit to top 5 results
            
            // Display search results
            const resultsContainer = document.getElementById('search-results');
            if (resultsContainer) {
                resultsContainer.innerHTML = '';
                
                if (searchTerm.length > 0 && results.length > 0) {
                    results.forEach(result => {
                        const country = result.properties;
                        const isoCode = getIsoCode(country);
                        
                        const resultItem = document.createElement('div');
                        resultItem.className = 'search-result-item';
                        resultItem.innerHTML = `${country.name} ${isoCode.length === 2 ? getFlagEmoji(isoCode) : ''}`;
                        resultItem.onclick = () => {
                            // Find country on map and zoom to it
                            const bounds = L.geoJSON(result).getBounds();
                            mapInstance.fitBounds(bounds);
                            // Create a temporary marker
                            const center = bounds.getCenter();
                            const marker = L.marker(center).addTo(mapInstance);
                            setTimeout(() => mapInstance.removeLayer(marker), 2000);
                            // Clear search
                            searchInput.value = '';
                            resultsContainer.innerHTML = '';
                        };
                        resultsContainer.appendChild(resultItem);
                    });
                } else if (searchTerm.length > 0) {
                    resultsContainer.innerHTML = '<div class="no-results">No countries found</div>';
                }
            }
        });
    }
});