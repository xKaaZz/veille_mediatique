import React from 'react';
import Home from './pages/Home';
import logo from './assets/logo.png';

function App() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
            <div className="bg-white w-full max-w-6xl p-16 rounded-3xl shadow-2xl">
                <div className="flex justify-center mb-6">
                    <img src={logo} alt="Logo" className="w-40 h-40 rounded-full shadow-md" />
                </div>

                <h1 className="text-5xl font-bold text-blue-600 mb-8 text-center">
                    📰 Veille Médiatique
                </h1>

                <p className="text-lg text-gray-600 text-center mb-8">
                    Bienvenue sur votre plateforme de veille d'actualités.
                </p>

                <Home />
            </div>
        </div>
    );
}

export default App;
