import React, { useState, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import proj4 from "proj4";
import "./Map.css";

mapboxgl.accessToken = "";

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
    });

    const handleFieldClick = async (easting, northing, lng, lat) => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch("http://localhost:5000/get_data", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ easting, northing }),
        });

        if (!response.ok)
          throw new Error(`Error fetching data: ${response.statusText}`);

        const data = await response.json();
        setSidebarData({
          longitude: lng.toFixed(4), // Add longitude
          latitude: lat.toFixed(4), // Add latitude
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

    const updateMapWithField = (lng, lat) => {
      const fieldSize = 0.0005;
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
        map.addSource("detected-field", { type: "geojson", data: fieldGeoJSON });
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
      const [easting, northing] = proj4(WGS84, IRISH_GRID, [lng, lat]);

      updateMapWithField(lng, lat);
      handleFieldClick(easting, northing, lng, lat); // Pass lng and lat here
      setIsSidebarOpen(true);

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
          <button className="close-button" onClick={() => setIsSidebarOpen(false)}>
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
              <hr />
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
              <hr />
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
              <hr />
              <h5>Elevation</h5>
              {sidebarData.elevation ? (
                <p><strong>Elevation:</strong> {sidebarData.elevation.Elevation} m</p>
              ) : (
                <p>No elevation data available.</p>
              )}
              <hr />
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
              <hr />
              {sidebarData.cluster_prediction !== undefined ? (
                <div>
                  <h5>Cluster Prediction</h5>
                  <p><strong>Predicted Cluster:</strong> {sidebarData.cluster_prediction}</p>
                </div>
              ) : sidebarData.cluster_prediction_error ? (
                <div>
                  <h5>Cluster Prediction</h5>
                  <p className="error">{sidebarData.cluster_prediction_error}</p>
                </div>
              ) : null}
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
