// Initialize the map
const map = L.map('map').setView([51.505, -0.09], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Create layer groups for markers and polygons
const markersLayer = L.layerGroup().addTo(map);
const polygonsLayer = L.layerGroup().addTo(map);

// Function to submit the query
function submitQuery() {
    const query = document.getElementById('query-input').value;
    fetch('/query', {
        method: 'POST',
        body: new FormData(document.querySelector('form')),
    })
    .then(response => response.json())
    .then(data => displayMapData(data))
    .catch(error => console.error('Error:', error));
}

// Function to display the map data
function displayMapData(data) {
    // Clear previous layers from the map
    markersLayer.clearLayers();
    polygonsLayer.clearLayers();

    // Zoom and pan the map to the bounds
    if (data.bounds) {
        map.fitBounds(data.bounds);
    }

    // Parse the received map data and display it on the map
    data.data.elements.forEach(element => {
        if (element.type === "node") {
            const marker = L.marker([element.lat, element.lon]);
            marker.addTo(markersLayer);
        } else if (element.type === "way" && element.nodes) {
            const latLngs = element.nodes.map(node => {
                const nodeElement = data.data.elements.find(e => e.type === "node" && e.id === node);
                return [nodeElement.lat, nodeElement.lon];
            });
            const polygon = L.polygon(latLngs, { color: 'blue' });
            polygon.addTo(polygonsLayer);
        }
    });
}

// Add event listener for the submit button
document.getElementById('submit-btn').addEventListener('click', submitQuery);
