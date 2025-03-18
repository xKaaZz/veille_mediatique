import React from 'react';

export const Card = ({ children }) => (
    <div className="bg-white p-4 rounded shadow">
        {children}
    </div>
);

export const CardContent = ({ children }) => (
    <div className="p-2">
        {children}
    </div>
);
