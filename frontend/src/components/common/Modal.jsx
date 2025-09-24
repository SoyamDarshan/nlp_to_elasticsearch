import React from "react";
import './common.css';

const Modal = ({ head, content, onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{head}</h2>
          <button onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          {typeof content === "function" || React.isValidElement(content)
            ? content
            : <div>{content}</div>}
        </div>
      </div>
    </div>
  );
};

export default Modal;
