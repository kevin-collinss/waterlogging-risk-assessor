import React, { useState, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import proj4 from "proj4";
import "./Map.css";

mapboxgl.accessToken =
  "pk.eyJ1Ijoia2V2aW5jb2wiLCJhIjoiY20zazJ2dTF2MDhqNDJzcGVwdm1rbnlkYyJ9.cVBc9ZK9hR92V6o3vDWz5g";

const WGS84 = "EPSG:4326"; // WGS84 (Longitude, Latitude)
const IRISH_GRID = "EPSG:29903";

// Define projections (Irish Grid, meters)
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
    // Initialize the map with a flat, north-up view:
    const map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/satellite-streets-v11",
      center: [-8, 53],
      zoom: 5,
      pitch: 0,
      bearing: 0,
    });

    // Disable rotation (for a pure overhead view)
    map.dragRotate.disable();
    map.touchZoomRotate.disableRotation();

    // When the map loads, add an image source for the stamp.
    // Initially, we set dummy coordinates.
    map.on("load", () => {
      // Add the image source. Ensure the image exists at public/images/soil_gathering.png
      map.addSource("stamp-source", {
        type: "image",
        url: "/images/soil_gathering_circle.png",
        coordinates: [
          [-7.6921, 53.1424],
          [-7.6911, 53.1424],
          [-7.6911, 53.1414],
          [-7.6921, 53.1414],
        ],
      });
      // Add a raster layer to display the image source.
      map.addLayer({
        id: "stamp-layer",
        type: "raster",
        source: "stamp-source",
        paint: {
          "raster-opacity": 1,
        },
      });
    });

    // Function to fetch field data from your backend.
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

    // This function computes the 50m square corners around the clicked point.
    // It converts the clicked point (WGS84) to IRISH_GRID, subtracts and adds 25m,
    // then converts the resulting corners back to WGS84.
    const updateStampImageCoordinates = (lng, lat) => {
      // Convert the clicked coordinate from WGS84 to IRISH_GRID (meters)
      const [easting, northing] = proj4(WGS84, IRISH_GRID, [lng, lat]);
      const halfSize = 50;
      // Calculate the four corners in IRISH_GRID (meters)
      const topLeftMeters = [easting - halfSize, northing + halfSize];
      const topRightMeters = [easting + halfSize, northing + halfSize];
      const bottomRightMeters = [easting + halfSize, northing - halfSize];
      const bottomLeftMeters = [easting - halfSize, northing - halfSize];

      // Convert each corner back to WGS84 (lng, lat)
      const tl = proj4(IRISH_GRID, WGS84, topLeftMeters);
      const tr = proj4(IRISH_GRID, WGS84, topRightMeters);
      const br = proj4(IRISH_GRID, WGS84, bottomRightMeters);
      const bl = proj4(IRISH_GRID, WGS84, bottomLeftMeters);

      // Coordinates must be in the order: top-left, top-right, bottom-right, bottom-left.
      const newCoordinates = [tl, tr, br, bl];

      // Update the image source's coordinates.
      const stampSource = map.getSource("stamp-source");
      if (stampSource) {
        stampSource.setCoordinates(newCoordinates);
      }
    };

    // When the map is clicked:
    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      // Update the stamp image to cover a 50m square centered at the click point.
      updateStampImageCoordinates(lng, lat);

      // Convert the clicked point for backend query.
      const [easting, northing] = proj4(WGS84, IRISH_GRID, [lng, lat]);
      handleFieldClick(easting, northing, lng, lat);
      setIsSidebarOpen(true);
      map.flyTo({ center: [lng, lat], zoom: 16 });
    });

    return () => map.remove();
  }, []);

  return (
    <div className="map-container">
      <header className="map-header">
        <div className="header-left">
          <a href="/about" className="header-about-link">
            About
          </a>
        </div>
        <div className="header-center">
          <img
            src="/images/waterlogging_logo.png"
            alt="Waterlogging Logo"
            className="header-logo"
          />
        </div>
        <div className="header-right"></div>
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
              {sidebarData.cluster_prediction !== undefined ? (
                <div className="cluster-prediction">
                  <h5>Cluster Prediction</h5>
                  <p>
                    <strong>Predicted Cluster:</strong>{" "}
                    {sidebarData.cluster_prediction}
                  </p>
                </div>
              ) : sidebarData.cluster_prediction_error ? (
                <div className="cluster-prediction error">
                  <h5>Cluster Prediction</h5>
                  <p>{sidebarData.cluster_prediction_error}</p>
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
                    <strong>Material Description:</strong>{" "}
                    {sidebarData.hydrology.ParMat_Des}
                  </p>
                  <p>
                    <strong>Drainage:</strong>{" "}
                    {sidebarData.hydrology.SoilDraina}
                  </p>
                </>
              ) : (
                <p>No hydrology data available.</p>
              )}
              <hr />
              <h5>Elevation</h5>
              {sidebarData.elevation ? (
                <p>
                  <strong>Elevation:</strong> {sidebarData.elevation.Elevation}{" "}
                  m
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
