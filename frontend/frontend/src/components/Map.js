import React, { useState, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import proj4 from "proj4";
import "./Map.css";

mapboxgl.accessToken ="pk.eyJ1Ijoia2V2aW5jb2wiLCJhIjoiY20zazJ2dTF2MDhqNDJzcGVwdm1rbnlkYyJ9.cVBc9ZK9hR92V6o3vDWz5g";

const WGS84 = "EPSG:4326"; // WGS84 (Longitude, Latitude)
const IRISH_GRID = "EPSG:29903";

// Define projections
proj4.defs(
  "EPSG:29903",
  "+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=1.000035 +x_0=200000 +y_0=250000 +ellps=airy +units=m +no_defs"
);

const Map = () => {
  const [sidebarData, setSidebarData] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/satellite-streets-v11",
      center: [-7.6921, 53.1424],
      zoom: 15,
      pitch: 0,
      bearing: 0,
    });

    let stampMarker = null; // Store the stamp marker so it can be replaced on new clicks

    const handleFieldClick = async (easting, northing, lng, lat) => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("http://localhost:5000/get_data", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ easting, northing }),
        });

        if (!response.ok)
          throw new Error(`Error fetching data: ${response.statusText}`);

        const data = await response.json();
        setSidebarData({
          longitude: lng.toFixed(4),
          latitude: lat.toFixed(4),
          easting: easting.toFixed(2),
          northing: northing.toFixed(2),
          soil: data.soil_data || null,
          hydrology: data.hydrology_data || null,
          elevation: data.elevation_data || null,
          rainfall: data.rainfall_data || null,
          cluster_prediction: data.cluster_prediction,
          cluster_prediction_error: data.cluster_prediction_error,
        });
      } catch (err) {
        setError("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      // Convert from WGS84 to IRISH_GRID
      const [easting, northing] = proj4(WGS84, IRISH_GRID, [lng, lat]);

      // Remove existing stamp marker if it exists
      if (stampMarker) {
        stampMarker.remove();
      }

      // Create a custom element for the stamp marker
      const stampEl = document.createElement("div");
      stampEl.className = "stamp-marker";
      stampEl.style.backgroundImage = "url('/images/soil_gathering.png')";
      stampEl.style.width = "50px";
      stampEl.style.height = "50px";
      stampEl.style.backgroundSize = "contain";
      stampEl.style.backgroundRepeat = "no-repeat";
      // Optionally add a border to help debug positioning
      // stampEl.style.border = "2px solid red";

      // Create the marker with no offset and anchor it by center
      stampMarker = new mapboxgl.Marker({
        element: stampEl,
        anchor: "center",
        offset: [0, 0],
      })
        .setLngLat([lng, lat])
        .addTo(map);

      // Fetch data and update sidebar
      handleFieldClick(easting, northing, lng, lat);
      setIsSidebarOpen(true);

      map.flyTo({ center: [lng, lat], zoom: 16 });
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
          <button className="close-button" onClick={() => setIsSidebarOpen(false)}>
            &times;
          </button>
          {loading ? (
            <p>Loading data...</p>
          ) : error ? (
            <p className="error">{error}</p>
          ) : sidebarData ? (
            <div className="sidebar-content">
              {sidebarData.cluster_prediction !== undefined ? (
                <div>
                  <h5>Cluster Prediction</h5>
                  <p>
                    <strong>Predicted Cluster:</strong> {sidebarData.cluster_prediction}
                  </p>
                </div>
              ) : sidebarData.cluster_prediction_error ? (
                <div>
                  <h5>Cluster Prediction</h5>
                  <p className="error">{sidebarData.cluster_prediction_error}</p>
                </div>
              ) : null}
              <hr />
              <p>
                <strong>Longitude:</strong> {sidebarData.longitude}
              </p>
              <p>
                <strong>Latitude:</strong> {sidebarData.latitude}
              </p>
              <p>
                <strong>Easting:</strong> {sidebarData.easting}
              </p>
              <p>
                <strong>Northing:</strong> {sidebarData.northing}
              </p>
              <hr />
              <h5>Soil Data</h5>
              {sidebarData.soil ? (
                <>
                  <p>
                    <strong>Texture:</strong> {sidebarData.soil.Texture_Su}
                  </p>
                  <p>
                    <strong>Depth:</strong> {sidebarData.soil.DEPTH}
                  </p>
                  <p>
                    <strong>Description:</strong> {sidebarData.soil.PlainEngli}
                  </p>
                </>
              ) : (
                <p>No soil data available.</p>
              )}
              <hr />
              <h5>Hydrology Data</h5>
              {sidebarData.hydrology ? (
                <>
                  <p>
                    <strong>Category:</strong> {sidebarData.hydrology.CATEGORY}
                  </p>
                  <p>
                    <strong>Material Description:</strong> {sidebarData.hydrology.ParMat_Des}
                  </p>
                  <p>
                    <strong>Drainage:</strong> {sidebarData.hydrology.SoilDraina}
                  </p>
                </>
              ) : (
                <p>No hydrology data available.</p>
              )}
              <hr />
              <h5>Elevation</h5>
              {sidebarData.elevation ? (
                <p>
                  <strong>Elevation:</strong> {sidebarData.elevation.Elevation} m
                </p>
              ) : (
                <p>No elevation data available.</p>
              )}
              <hr />
              <h5>Rainfall</h5>
              {sidebarData.rainfall ? (
                <>
                  <p>
                    <strong>Annual:</strong> {sidebarData.rainfall.ANN} mm
                  </p>
                  <p>
                    <strong>Winter:</strong> {sidebarData.rainfall.DJF} mm
                  </p>
                  <p>
                    <strong>Spring:</strong> {sidebarData.rainfall.MAM} mm
                  </p>
                  <p>
                    <strong>Summer:</strong> {sidebarData.rainfall.JJA} mm
                  </p>
                  <p>
                    <strong>Autumn:</strong> {sidebarData.rainfall.SON} mm
                  </p>
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
