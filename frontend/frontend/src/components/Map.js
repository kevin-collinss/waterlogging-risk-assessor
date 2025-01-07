import React, { useState, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import proj4 from "proj4";
import "./Map.css";

mapboxgl.accessToken = "pk.eyJ1Ijoia2V2aW5jb2wiLCJhIjoiY20zazJ2dTF2MDhqNDJzcGVwdm1rbnlkYyJ9.cVBc9ZK9hR92V6o3vDWz5g";

// Define projections
const WGS84 = "EPSG:4326"; // WGS84 (Longitude, Latitude)
const ITM = "EPSG:2157"; // Irish Transverse Mercator (ITM)

// Define ITM projection using Proj4 string (specific to Ireland)
proj4.defs(
  ITM,
  "+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=0.99982 +x_0=600000 +y_0=750000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
);

const Map = () => {
  const [sidebarData, setSidebarData] = useState(null); // Holds fetched data
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Sidebar visibility
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error message state

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/satellite-streets-v11",
      center: [-7.6921, 53.1424],
      zoom: 15,
    });

    const handleFieldClick = async (easting, northing) => {
      setLoading(true); // Start loading
      setError(null); // Clear previous errors
      console.log(`Fetching data for Easting: ${easting}, Northing: ${northing}`);

      try {
        const response = await fetch("http://localhost:5000/get_data", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ easting, northing }),
        });

        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Data fetched successfully:", data);

        // Update sidebar data
        setSidebarData({
          easting,
          northing,
          soil: data.soil_data || null,
          hydrology: data.hydrology_data || null,
          elevation: data.elevation_data || null,
          rainfall: data.rainfall_data || null,
        });
      } catch (err) {
        console.error("Error fetching data:", err.message);
        setError("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false); // Stop loading
      }
    };

    const updateMapWithField = (lng, lat) => {
      const fieldSize = 0.0005; // Approximate field size
      const fieldGeoJSON = {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [
                [
                  [lng - fieldSize, lat - fieldSize],
                  [lng + fieldSize, lat - fieldSize],
                  [lng + fieldSize, lat + fieldSize],
                  [lng - fieldSize, lat + fieldSize],
                  [lng - fieldSize, lat - fieldSize],
                ],
              ],
            },
            properties: { name: "Detected Field" },
          },
        ],
      };

      if (map.getSource("detected-field")) {
        map.getSource("detected-field").setData(fieldGeoJSON);
      } else {
        map.addSource("detected-field", {
          type: "geojson",
          data: fieldGeoJSON,
        });

        map.addLayer({
          id: "detected-field-fill",
          type: "fill",
          source: "detected-field",
          paint: {
            "fill-color": "#f00",
            "fill-opacity": 0.5,
          },
        });

        map.addLayer({
          id: "detected-field-border",
          type: "line",
          source: "detected-field",
          paint: {
            "line-color": "#000",
            "line-width": 2,
          },
        });
      }
    };

    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      const [easting, northing] = proj4(WGS84, ITM, [lng, lat]);
      console.log(`Clicked at Longitude: ${lng}, Latitude: ${lat}`);

      // Show detected field
      updateMapWithField(lng, lat);

      // Open the sidebar
      setSidebarData({
        longitude: lng.toFixed(4),
        latitude: lat.toFixed(4),
        easting: easting.toFixed(2),
        northing: northing.toFixed(2),
      });
      setIsSidebarOpen(true);

      // Fetch additional data
      handleFieldClick(easting, northing);

      map.flyTo({
        center: [lng, lat],
        zoom: 16,
      });
    });

    return () => map.remove();
  }, []);

  return (
    <div className="map-container">
      <header className="map-header">
        <h1>Flood Risk Classifier</h1>
        <p>Click on your field to classify flood risk.</p>
      </header>
      <div className="map-content">
        <div id="map"></div>
        <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
          <button
            className="close-button"
            onClick={() => setIsSidebarOpen(false)}
          >
            &times;
          </button>
          {loading ? (
            <p>Loading data...</p>
          ) : error ? (
            <p className="error">{error}</p>
          ) : sidebarData ? (
            <div className="sidebar-content">
              <h4>Field Information</h4>
              <p><strong>Longitude:</strong> {sidebarData.longitude}</p>
              <p><strong>Latitude:</strong> {sidebarData.latitude}</p>
              <p><strong>Easting:</strong> {sidebarData.easting}</p>
              <p><strong>Northing:</strong> {sidebarData.northing}</p>
              <h5>Soil Data</h5>
              {sidebarData.soil ? (
                <>
                  <p><strong>Texture:</strong> {sidebarData.soil.Texture_Su}</p>
                  <p><strong>Depth:</strong> {sidebarData.soil.DEPTH}</p>
                  <p><strong>Description:</strong> {sidebarData.soil.PlainEngli}</p>
                </>
              ) : (
                <p>No soil data available.</p>
              )}
              <h5>Hydrology Data</h5>
              {sidebarData.hydrology ? (
                <>
                  <p><strong>Category:</strong> {sidebarData.hydrology.CATEGORY}</p>
                  <p><strong>Material Description:</strong> {sidebarData.hydrology.ParMat_Des}</p>
                  <p><strong>Drainage:</strong> {sidebarData.hydrology.SoilDraina}</p>
                </>
              ) : (
                <p>No hydrology data available.</p>
              )}
              <h5>Elevation</h5>
              {sidebarData.elevation ? (
                <p><strong>Elevation:</strong> {sidebarData.elevation.Elevation} m</p>
              ) : (
                <p>No elevation data available.</p>
              )}
              <h5>Rainfall</h5>
              {sidebarData.rainfall ? (
                <>
                  <p><strong>Annual:</strong> {sidebarData.rainfall.ANN} mm</p>
                  <p><strong>Winter:</strong> {sidebarData.rainfall.DJF} mm</p>
                  <p><strong>Spring:</strong> {sidebarData.rainfall.MAM} mm</p>
                  <p><strong>Summer:</strong> {sidebarData.rainfall.JJA} mm</p>
                  <p><strong>Autumn:</strong> {sidebarData.rainfall.SON} mm</p>
                </>
              ) : (
                <p>No rainfall data available.</p>
              )}
            </div>
          ) : (
            <p>No data available. Click a field to fetch data.</p>
          )}
        </aside>
      </div>
      <footer className="map-footer">
        <p>Powered by Mapbox | Irish Transverse Mercator Projection</p>
      </footer>
    </div>
  );
};

export default Map;
