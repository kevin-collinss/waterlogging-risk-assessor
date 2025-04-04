import React from "react";
import { Link } from "react-router-dom";
import "./Map.css";

const Home = () => {
  return (
    <div className="home-container">
      <div className="home-left" style={{ backgroundImage: "url('/images/geometric-leaves.png')", backgroundRepeat: "repeat", backgroundSize: "auto", backgroundBlendMode: "multiply"}}>
        <img
          src="/images/waterlogging_logo.png"
          alt="Waterlogging Risk Classifier Logo"
          className="home-logo"
        />
      </div>

      <div className="home-right" >
        <div className="home-text">
          <h1>Know Your Land</h1>
          <p>
            This tool helps farmers, researchers, and planners understand flood
            and waterlogging risk across agricultural land in Ireland. Using
            real-world environmental data and unsupervised machine learning, it
            highlights potential problem areas based on soil type, elevation,
            hydrology, and rainfall.
            <br />
            <br />
            Simply click on a location on the interactive map to explore
            detailed environmental and risk information for that area. The tool
            will instantly show relevant insights including soil texture,
            elevation, drainage characteristics, rainfall patterns, and
            predicted flood risk classification.
          </p>

          <div style={{ marginTop: "40px" }}>
            <Link to="/map" className="home-start-button">
              Launch Tool →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
