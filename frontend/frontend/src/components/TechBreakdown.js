import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'; 
import { Link } from 'react-router-dom';
import 'github-markdown-css'; 

const TechBreakdown = () => {
  const [markdown, setMarkdown] = useState('');

  useEffect(() => {
    fetch('/docs/tech_breakdown.md')
      .then((res) => res.text())
      .then((text) => setMarkdown(text));
  }, []);

  return (
    <div style={{ padding: '40px' }}>
      <Link to="/map" className="fixed-back-button">
        ← Back to Map
      </Link>

      <div className="markdown-body" style={{ marginTop: '20px' }}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {markdown}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default TechBreakdown;
