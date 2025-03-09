// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// Adjust these paths to match your folder structure:
import Map from "./components/Map";
import TechBreakdown from "./components/TechBreakdown";

function App() {
  return (
    <Router>
      <Routes>
        {/* Show Map component at the root URL */}
        <Route path="/" element={<Map />} />
        {/* Show TechBreakdown at /tech-breakdown */}
        <Route path="/tech-breakdown" element={<TechBreakdown />} />
      </Routes>
    </Router>
  );
}

export default App;
