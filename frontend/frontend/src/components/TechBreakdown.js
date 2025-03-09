// src/components/TechBreakdown.js
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Link } from 'react-router-dom';

const TechBreakdown = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    fetch('/docs/tech_breakdown.md')
      .then((res) => res.text())
      .then((text) => setMarkdown(text));
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Montserrat, sans-serif' }}>
      {/* Link back to the Map page */}
      <Link to="/" style={{ textDecoration: 'none', color: '#8e704d', fontWeight: 'bold' }}>
        ← Back to Map
      </Link>
      <h1>Tech Breakdown</h1>
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
};

export default TechBreakdown;
