import React, { useState } from 'react';
import Dashboard from "../components/Dashboard";
import FlashNewsCard from "../components/FlashNewsCard";
import SummaryCard from "../components/SummaryCard";


export default function Home() {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    const handleGenerateSummary = () => {
        // TODO: Déclencher le workflow back-end pour générer le résumé personnalisé
        console.log("🚀 TODO: Lancer le workflow avec les dates :", startDate, endDate);
    };

    const handleGenerateDailySummary = () => {
        // TODO: Déclencher le workflow back-end pour générer le résumé des dernières 24h
        console.log("🚀 TODO: Lancer le workflow pour les dernières 24h");
    };

    const handleGenerateFlashNews = () => {
        // TODO: Déclencher le workflow back-end pour générer le mode "Flash News"
        console.log("🚀 TODO: Lancer le workflow Flash News");
    };

    return (
        <div className="container">
            <h1 className="text-3xl font-bold">📰 Veille Médiatique</h1>

            {/* Dashboard : Juste pour le résumé quotidien */}
            <Dashboard onGenerateDailySummary={handleGenerateDailySummary} />

            {/* Composants séparés pour plus de clarté */}
            <SummaryCard
                startDate={startDate}
                endDate={endDate}
                setStartDate={setStartDate}
                setEndDate={setEndDate}
                onGenerate={handleGenerateSummary}
            />

            <FlashNewsCard onGenerate={handleGenerateFlashNews} />
        </div>
    );
    
}
