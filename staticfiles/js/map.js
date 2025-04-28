// Global map instance to prevent multiple initializations
let mapInstance = null;

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
        const isoCode = props ? (props.iso_a2 || props.ISO_A2 || props.iso_a3 || '') : '';
        this._div.innerHTML = '<h4>Country Info</h4>' + (props ?
            '<b>' + props.name + '</b><br />ISO: ' + isoCode :
            'Hover over a country');
    };
    info.addTo(mapInstance);

    // Fetch countries and visits
    let countriesGeoJSON, visits = [];
    const visitedCountriesList = document.getElementById('visited-countries');
    const wantToVisitCountriesList = document.getElementById('want-to-visit-countries');

    // Function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Fetch all GeoJSON data first
    fetch('/static/js/countries.geojson')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch GeoJSON');
            return response.json();
        })
        .then(geojson => {
            console.log("GeoJSON loaded successfully");
            countriesGeoJSON = geojson;
            
            // Then fetch user visits
            return fetch('/countries/api/visits/');
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
            console.error('Error initializing map data:', error);
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
                // Get ISO code from various possible properties
                const isoCode = feature.properties.iso_a2 || 
                               feature.properties.ISO_A2 || 
                               feature.properties.iso_a3;
                
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
                // Get country details from properties
                const countryName = feature.properties.name;
                const isoCode = feature.properties.iso_a2 || 
                              feature.properties.ISO_A2 || 
                              feature.properties.iso_a3;
                
                if (!isoCode) {
                    console.warn(`No ISO code found for ${countryName}`);
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
                            alert('Error: This country does not have a valid ISO code');
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
            moveBtn.onclick = () => updateVisit(visit.country.iso_code, 'want_to_visit');
            btnGroup.appendChild(moveBtn);
        } else {
            // In want to visit list, add "mark as visited" button
            const visitedBtn = document.createElement('button');
            visitedBtn.className = 'btn btn-outline-success';
            visitedBtn.innerHTML = '<i class="fas fa-check"></i>';
            visitedBtn.title = 'Mark as Visited';
            visitedBtn.onclick = () => updateVisit(visit.country.iso_code, 'visited');
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

    function createVisit(isoCode, status) {
        console.log(`Creating visit for ${isoCode} with status ${status}`);
        
        fetch('/countries/api/visits/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ iso_code: isoCode, status: status }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to create visit: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Visit created successfully:', data);
            visits.push(data);
            mapInstance.closePopup();
            showNotification(`Country marked as ${status === 'visited' ? 'visited' : 'want to visit'}`);
            updateMap();
            updateLists();
        })
        .catch(error => {
            console.error('Error creating visit:', error);
            showNotification('Failed to mark country. Please try again.', 'danger');
        });
    }

    function updateVisit(isoCode, status) {
        console.log(`Updating visit for ${isoCode} to ${status}`);
        
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

    // Make functions available globally
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

    window.removeCountry = function(isoCode) {
        removeCountry(isoCode);
    };
});