import React from 'react';

export const DatePicker = ({ value, onChange, placeholder }) => {
    return (
        <input
            type="date"
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            max={new Date().toISOString().split('T')[0]}  // Limite la date au jour actuel
            className="border p-2 rounded"
        />
    );
};
