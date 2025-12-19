import React from 'react';
import PropTypes from 'prop-types';
import './ErrorMessage.css';

function ErrorMessage({ message, onDismiss }) {
    if (!message) return null;

    return (
        <div className="error-message" role="alert">
            <div className="error-content">
                <span className="error-icon">⚠️</span>
                <p>{message}</p>
                {onDismiss && (
                    <button
                        className="error-dismiss"
                        onClick={onDismiss}
                        aria-label="Dismiss error"
                    >
                        ×
                    </button>
                )}
            </div>
        </div>
    );
}

ErrorMessage.propTypes = {
    message: PropTypes.string,
    onDismiss: PropTypes.func,
};

export default ErrorMessage;
