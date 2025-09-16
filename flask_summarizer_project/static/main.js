document.addEventListener('DOMContentLoaded', () => {
    // Dummy Data - In a real app, this would be fetched from a Flask endpoint
    const cities = [
        { id: 1, name: 'תל אביב', aqi: 78, population: '460,000', factories: 12, trees: '85K', cars: 180, lat: 32.0853, lng: 34.7818 },
        { id: 2, name: 'חיפה', aqi: 95, population: '285,000', factories: 25, trees: '95K', cars: 120, lat: 32.7940, lng: 34.9896 },
        { id: 3, name: 'באר שבע', aqi: 72, population: '209,000', factories: 6, trees: '45K', cars: 85, lat: 31.2518, lng: 34.7913 },
        { id: 4, name: 'רמת גן', aqi: 82, population: '163,000', factories: 4, trees: '65K', cars: 95, lat: 32.0718, lng: 34.8083 },
        { id: 5, name: 'פתח תקווה', aqi: 75, population: '247,000', factories: 7, trees: '70K', cars: 110, lat: 32.0886, lng: 34.8814 },
        { id: 6, name: 'אשדוד', aqi: 88, population: '225,000', factories: 15, trees: '55K', cars: 90, lat: 31.7967, lng: 34.6547 },
        { id: 7, name: 'נתניה', aqi: 70, population: '221,000', factories: 5, trees: '60K', cars: 85, lat: 32.3168, lng: 34.8532 },
        { id: 8, name: 'בני ברק', aqi: 85, population: '204,000', factories: 3, trees: '35K', cars: 75, lat: 32.0862, lng: 34.8398 },
    ];

    // Initialize the Leaflet map
    const map = L.map('israel-map').setView([31.5, 34.8], 8);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markers = [];

    // Function to update the map with markers
    const updateMap = (filteredCities) => {
        markers.forEach(marker => map.removeLayer(marker));
        markers.length = 0;

        filteredCities.forEach(city => {
            const markerColor = city.aqi > 80 ? 'red' : 'green';
            const marker = L.circleMarker([city.lat, city.lng], {
                radius: 10,
                fillColor: markerColor,
                color: '#fff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);

            marker.on('click', () => showCityModal(city));
            markers.push(marker);
        });
    };

    // Function to render the city list
    const renderCityList = (filteredCities) => {
        const cityListContainer = document.getElementById('city-list');
        cityListContainer.innerHTML = '';
        filteredCities.forEach(city => {
            const cityItem = document.createElement('div');
            cityItem.className = 'city-item';
            cityItem.innerHTML = `
                <div class="city-name">${city.name}</div>
                <div class="aqi-score">${city.aqi} AQI</div>
            `;
            cityListContainer.appendChild(cityItem);
        });
    };

    // Filter logic
    const filterData = () => {
        const aqiMin = parseInt(document.getElementById('aqi-min').value);
        const aqiMax = parseInt(document.getElementById('aqi-max').value);

        const filteredCities = cities.filter(city => {
            return city.aqi >= aqiMin && city.aqi <= aqiMax;
        });

        updateMap(filteredCities);
        renderCityList(filteredCities);
    };

    // Slider event listeners
    document.getElementById('aqi-min').addEventListener('input', filterData);
    document.getElementById('aqi-max').addEventListener('input', filterData);
    
    // Initial render
    updateMap(cities);
    renderCityList(cities);

    // Modal functionality
    const modal = document.getElementById('city-details-modal');
    const closeBtn = document.querySelector('.close-button');

    const showCityModal = (city) => {
        const modalData = document.getElementById('modal-data');
        modalData.innerHTML = `
            <h3>נתוני העיר: ${city.name}</h3>
            <p><strong>AQI:</strong> ${city.aqi}</p>
            <p><strong>אוכלוסייה:</strong> ${city.population}</p>
            <p><strong>מפעלים:</strong> ${city.factories}</p>
        `;
        modal.style.display = 'flex';
    };

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
});