import React from "react";
import './common.css';

// Helper to check if all objects in array share the same keys
function allObjectsShareKeys(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return false;
  const keys = Object.keys(arr[0]);
  return arr.every(obj =>
    typeof obj === "object" &&
    Object.keys(obj).length === keys.length &&
    keys.every(k => Object.prototype.hasOwnProperty.call(obj, k))
  );
}

const MAX_DEPTH = 5;
const KeyValueDisplay = ({ data, depth = 0, seen = new WeakSet() }) => {
  if (depth > MAX_DEPTH) {
    // At max depth, show a summary of the data instead of a message
    if (Array.isArray(data)) {
      // Show a comma-separated list of primitive values or keys for objects
      if (data.length === 0) return <div>[Array: empty]</div>;
      if (data.every(v => v === null || typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean')) {
        return <div>[{data.map(v => String(v)).join(', ')}]</div>;
      } else if (data.every(v => typeof v === 'object' && v !== null)) {
        // Array of objects: show keys summary
        const keys = Array.from(new Set(data.flatMap(obj => Object.keys(obj))));
        return <div>[Array of objects: keys = {keys.join(', ')}]</div>;
      } else {
        return <div>[Array: {data.length} items]</div>;
      }
    } else if (typeof data === 'object' && data !== null) {
      // Object: show keys
      const keys = Object.keys(data);
      return <div>[Object: keys = {keys.join(', ')}]</div>;
    } else {
      // Primitive
      return <div>{String(data)}</div>;
    }
  }
  if (typeof data === 'object' && data !== null) {
    if (seen.has(data)) {
      return <div style={{ color: 'red' }}>[Circular]</div>;
    }
    seen.add(data);
  }
  // Patch: If array of objects with only primitive values, render as table (fixes React error #31)
  if (Array.isArray(data) && data.length > 0 && allObjectsShareKeys(data)) {
    const keys = Object.keys(data[0]);
    // Check if all values in all rows are primitives (string, number, boolean, null)
    const allPrimitive = data.every(row =>
      keys.every(key => {
        const v = row[key];
        return (
          v === null ||
          typeof v === 'string' ||
          typeof v === 'number' ||
          typeof v === 'boolean'
        );
      })
    );
    if (allPrimitive) {
      return (
        <table className="kv-table">
          <thead>
            <tr>
              {keys.map(key => <th key={key}>{key}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                {keys.map(key => {
                  const v = row[key];
                  if (
                    v === null ||
                    typeof v === 'string' ||
                    typeof v === 'number' ||
                    typeof v === 'boolean'
                  ) {
                    return <td key={key}>{String(v)}</td>;
                  } else {
                    // Render objects/arrays as JSON string or recursively
                    return <td key={key}><KeyValueDisplay data={v} depth={depth + 1} seen={seen} /></td>;
                  }
                })}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }
    // Otherwise, fallback to rendering each row as key-value
    return (
      <div>
        {data.map((row, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            <KeyValueDisplay data={row} depth={depth + 1} seen={seen} />
          </div>
        ))}
      </div>
    );
  }
  // Render as key: value pairs
  if (typeof data === "object" && data !== null) {
    return (
      <div className="kv-list">
        {Object.entries(data).map(([k, v]) => (
          <div key={k} className="kv-item">
            <strong>{k}:</strong> {Array.isArray(v) || typeof v === "object" ? <KeyValueDisplay data={v} depth={depth + 1} seen={seen} /> : String(v)}
          </div>
        ))}
      </div>
    );
  }
  // Fallback for primitives
  return <div>{String(data)}</div>;
};

export default KeyValueDisplay;
