import React from 'react';
import './PopUp.css';

const PopUp = ({isOpen, onClose, message}) => {
    if (!isOpen) return null;

    return (
        <div className='popup-overlay'>
            <div className='popup-content'>
                <div className='popup-header'>
                    If Fluid Allowance is Less than Protocol Advises:
                </div>
                <p>{message}</p>
                <div className='button-row'>
                    <button className='cancel-button' onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
};

export default PopUp;