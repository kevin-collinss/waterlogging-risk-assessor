// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Adjust these paths to match your folder structure:
import Map from "./components/Map";
import TechBreakdown from "./components/TechBreakdown";
import LeafletPointMap from "./components/LeafletPointMap"; // NEW LINE

function App() {
  return (
    <Router>
      <Routes>
        {/* Original routes */}
        <Route path="/" element={<Map />} />
        <Route path="/tech-breakdown" element={<TechBreakdown />} />
        <Route path="/point-map" element={<LeafletPointMap />} />
      </Routes>
    </Router>
  );
}

export default App;
