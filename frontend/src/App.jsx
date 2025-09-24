import React, { useState } from 'react';
import SmartCanvas from './components/SmartCanvas';
import ErrorBoundary from './components/common/ErrorBoundary';
import './components/common/common.css';
import ShowAllESDocs from './components/ShowAllESDocs';

function App() {
  const [esSyncStatus, setEsSyncStatus] = useState(null);

  const handleRepopulateES = async () => {
    setEsSyncStatus('syncing');
    try {
      const response = await fetch('/api/repopulate-es', { method: 'POST' });
      const data = await response.json();
      if (data.status === 'success') {
        setEsSyncStatus('success');
      } else {
        setEsSyncStatus('error');
      }
    } catch (e) {
      setEsSyncStatus('error');
    }
  };
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [intent, setIntent] = useState('typeA');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('[Frontend] Submitting prompt:', prompt);
    const response = await fetch('/api/nlp-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    const data = await response.json();
    console.log('[Frontend] Received response:', data);
    setResults(data.results ? data.results : null);
    setIntent(data.intent);
    console.log('[Frontend] Updated intent:', data.intent, 'results:', data.results);
  };

  return (
    <div>
      <h1>NL Prompt to Elasticsearch</h1>
      <button onClick={handleRepopulateES} style={{marginBottom: 12}}>
        Repopulate Elasticsearch Index
      </button>
      {esSyncStatus === 'syncing' && <span style={{marginLeft: 8, color: '#888'}}>Syncing...</span>}
      {esSyncStatus === 'success' && <span style={{marginLeft: 8, color: 'green'}}>ES repopulated!</span>}
      {esSyncStatus === 'error' && <span style={{marginLeft: 8, color: 'red'}}>Error repopulating ES</span>}
      <ShowAllESDocs />
      <form onSubmit={handleSubmit}>
        <input
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Enter your query..."
        />
        <button type="submit">Submit</button>
      </form>
        <ErrorBoundary>
          <SmartCanvas intent={intent} results={results} />
        </ErrorBoundary>
    </div>
  );
}

export default App;
