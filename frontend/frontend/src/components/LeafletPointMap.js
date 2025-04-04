import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import Papa from "papaparse";
import proj4 from "proj4";
import "leaflet/dist/leaflet.css";
import { Link } from "react-router-dom";
import "./Map.css";

// Define projections
const WGS84 = "EPSG:4326";
const IRISH_GRID = "EPSG:29903";
proj4.defs(
  "EPSG:29903",
  "+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=1.000035 +x_0=200000 +y_0=250000 +ellps=airy +units=m +no_defs"
);

// Cluster colour scheme
const clusterColours = {
  0: "#49006a", // Dark purple
  1: "#2b8cbe", // Blue
  2: "#41ae76", // Green
  3: "#ffff33", // Yellow
};

const LeafletPointMap = () => {
  const [points, setPoints] = useState([]);

  useEffect(() => {
    Papa.parse("/data/training_data_with_clusters.csv", {
      download: true,
      header: true,
      complete: (result) => {
        const features = result.data
          .filter((row) => row.Easting && row.Northing && row.Cluster !== "")
          .map((row) => {
            const easting = parseFloat(row.Easting);
            const northing = parseFloat(row.Northing);
            const cluster = Math.floor(Number(row.Cluster));
            const [lng, lat] = proj4(IRISH_GRID, WGS84, [easting, northing]);
            return { lat, lng, cluster };
          });

        console.log("Parsed points:", features.slice(0, 5));
        setPoints(features);
      },
    });
  }, []);

  return (
    <div className="map-container">
      <header
        className="map-header leaflet-header"
        style={{
          backgroundColor: "#8e704d",
          backgroundImage: "url('/images/pipes.png')",
          backgroundRepeat: "repeat",
          backgroundSize: "auto",
          backgroundBlendMode: "multiply",
          color: "#ffffff",
        }}
      >
        <div className="header-left">
          <Link to="/map" className="back-button">
            ← Back to Main Map
          </Link>
        </div>

        <div className="header-center">
          <img
            src="/images/waterlogging_logo.png"
            alt="Waterlogging Logo"
            className="header-logo"
          />
        </div>

        <div className="header-right">
          <h2
            style={{ color: "white", textAlign: "right", marginRight: "15px" }}
          >
            Cluster Map View
          </h2>
        </div>
      </header>

      <div className="map-content">
        <MapContainer
          center={[53.5, -8]}
          zoom={7}
          scrollWheelZoom={true}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {points.map((point, index) => (
            <CircleMarker
              key={index}
              center={[point.lat, point.lng]}
              radius={0.8}
              pathOptions={{
                color: clusterColours[point.cluster] || "#888",
                fillOpacity: 0.9,
              }}
            />
          ))}
        </MapContainer>
      </div>

      <footer
        className="map-footer"
        style={{
          backgroundColor: "#8e704d",
          backgroundImage: "url('/images/pipes.png')",
          backgroundRepeat: "repeat",
          backgroundSize: "auto",
          backgroundBlendMode: "multiply",
          color: "#ffffff",
        }}
      >
        <p>
          Cluster visualisation via Leaflet | Irish Transverse Mercator
          Projection
        </p>
      </footer>
    </div>
  );
};

export default LeafletPointMap;
