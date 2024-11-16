import React, { useState, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import proj4 from "proj4";
import "./Map.css";

mapboxgl.accessToken = "";

// Define projections
const WGS84 = "EPSG:4326"; // WGS84 (Longitude, Latitude)
const ITM = "EPSG:2157"; // Irish Transverse Mercator (ITM)

// Define ITM projection using Proj4 string (specific to Ireland)
proj4.defs(
  ITM,
  "+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=0.99982 +x_0=600000 +y_0=750000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
);

const Map = () => {
  const [sidebarData, setSidebarData] = useState(null); // State for sidebar content
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // State for sidebar visibility

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: "map", // ID of the HTML element where the map will be rendered
      style: "mapbox://styles/mapbox/satellite-streets-v11", // Satellite view with streets
      center: [-7.6921, 53.1424], // Longitude, Latitude (Ireland's center)
      zoom: 15, // Zoomed closer to fields
    });

    const detectField = async (lng, lat) => {
      const fieldSize = 0.0005; // Approximate size of a field in degrees
      return {
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
            properties: {
              name: "Detected Field",
            },
          },
        ],
      };
    };

    const updateMapWithField = (geojsonField) => {
      if (map.getSource("detected-field")) {
        map.getSource("detected-field").setData(geojsonField);
      } else {
        map.addSource("detected-field", {
          type: "geojson",
          data: geojsonField,
        });

        map.addLayer({
          id: "detected-field-fill",
          type: "fill",
          source: "detected-field",
          paint: {
            "fill-color": "#f00", // Highlight color
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

    map.on("click", async (e) => {
      const { lng, lat } = e.lngLat;
      const [easting, northing] = proj4(WGS84, ITM, [lng, lat]);

      const detectedFieldGeoJSON = await detectField(lng, lat);
      updateMapWithField(detectedFieldGeoJSON);

      setSidebarData({
        longitude: lng.toFixed(4),
        latitude: lat.toFixed(4),
        easting: easting.toFixed(2),
        northing: northing.toFixed(2),
      });

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
        <p>CLick your field to classify your flood risk.</p>
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
          {sidebarData && (
            <div className="sidebar-content">
              <h4>Field Information</h4>
              <p><strong>Longitude:</strong> {sidebarData.longitude}</p>
              <p><strong>Latitude:</strong> {sidebarData.latitude}</p>
              <p><strong>Easting:</strong> {sidebarData.easting}</p>
              <p><strong>Northing:</strong> {sidebarData.northing}</p>
            </div>
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
