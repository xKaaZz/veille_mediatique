import React from 'react';

export function Button({ children, onClick, className = '' }) {
    return (
        <button
            onClick={onClick}
            className={`bg-blue-500 text-white px-6 py-3 rounded-lg text-lg 
                        hover:bg-blue-600 hover:scale-105 transition-all duration-200
                        active:scale-95 focus:ring-2 focus:ring-blue-300 ${className}`}
        >
            {children}
        </button>
    );
}