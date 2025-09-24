import React, { useState } from 'react';

export default function ShowAllESDocs({}) {
  const [docs, setDocs] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAllDocs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/nlp-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: 'show all' }),
      });
      const data = await response.json();
      // If backend returns a single object, wrap in array for display; if null, set to empty array
      if (!data.results) {
        setDocs([]);
      } else if (Array.isArray(data.results)) {
        setDocs(data.results);
      } else {
        setDocs([data.results]);
      }
    } catch (e) {
      setError('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{marginBottom: 16}}>
      <button onClick={fetchAllDocs} style={{marginBottom: 8}}>
        Show All Elasticsearch Documents
      </button>
      {loading && <div>Loading...</div>}
      {error && <div style={{color: 'red'}}>{error}</div>}
      {docs && docs.length > 0 && (
        <div style={{maxHeight: 400, overflow: 'auto', border: '1px solid #ccc', padding: 8, background: '#fafbfc'}}>
          <b>All Documents ({docs.length}):</b>
          <ul style={{fontSize: '0.95em'}}>
            {docs.map((doc, i) => (
              <li key={i} style={{marginBottom: 8}}>
                <pre style={{margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all'}}>{JSON.stringify(doc._source ? doc._source : doc, null, 2)}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}
      {docs && docs.length === 0 && !loading && (
        <div style={{color: '#888'}}>No documents found.</div>
      )}
    </div>
  );
}
