import React, { useState } from 'react';
import Modal from './common/Modal';
import KeyValueDisplay from './common/KeyValueDisplay';

export default function TemplateA({ results }) {
  // Modal state for details
  const [showModal, setShowModal] = useState(false);

  if (results) {
    return (
      <div className="template-a" style={{ background: 'linear-gradient(135deg, #e3f2fd 60%, #b3e5fc 100%)' }}>
        <h2>Template A</h2>
        <button onClick={() => setShowModal(true)} style={{marginBottom: 12}}>Show Details Modal</button>
        <div style={{ border: '1px solid #eee', padding: 12, borderRadius: 4 }}>
          <KeyValueDisplay data={results} depth={0} />
        </div>
        {showModal && (
          <Modal head="Details" content={<KeyValueDisplay data={results} depth={0} />} onClose={() => setShowModal(false)} />
        )}
      </div>
    );
  }
  return null;
}
