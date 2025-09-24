import React, { useState } from 'react';
import Modal from './common/Modal';
import KeyValueDisplay from './common/KeyValueDisplay';

export default function TemplateB({ results }) {
  const [showModal, setShowModal] = useState(false);
  if (results) {
    return (
      <div className="template-b" style={{ background: 'linear-gradient(135deg, #fff3e0 60%, #ffe0b2 100%)' }}>
        <h2>Template B</h2>
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
