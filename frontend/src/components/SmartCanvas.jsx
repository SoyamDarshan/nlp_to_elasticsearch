import React from 'react';
import TemplateA from './TemplateA';
import TemplateB from './TemplateB';
import KeyValueDisplay from './common/KeyValueDisplay';

function SmartCanvas({ results, intent }) {
  if (!results) {
    return <div style={{ color: '#888', fontStyle: 'italic' }}>No results to display.</div>;
  }
  // Debug: log results for inspection
  // eslint-disable-next-line no-console
  console.log('[SmartCanvas] Rendering results:', results);
  // If backend provides { template, data } structure, use it strictly
  if (results.template && results.data) {
    if (results.template === 'TemplateA') {
      return <div className="smart-canvas"><TemplateA results={results.data._source || results.data} intent={intent} /></div>;
    } else if (results.template === 'TemplateB') {
      return <div className="smart-canvas"><TemplateB results={results.data._source || results.data} intent={intent} /></div>;
    } else {
      return (
        <div className="smart-canvas" style={{ color: 'red', margin: '1em 0' }}>
          <div>[Unknown Template] Unexpected template: {results.template}</div>
          <KeyValueDisplay data={results.data} depth={0} />
        </div>
      );
    }
  }
  // fallback: try to infer
  if (results.cve) {
    return <div className="smart-canvas"><TemplateA results={results} intent={intent} /></div>;
  } else if (results.components) {
    return <div className="smart-canvas"><TemplateB results={results} intent={intent} /></div>;
  } else {
    // Fallback: render any object as key-value display
    return (
      <div className="smart-canvas">
  <KeyValueDisplay data={results} depth={0} />
      </div>
    );
  }
}

export default SmartCanvas;
