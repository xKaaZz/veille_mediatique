import React, { useState } from 'react';
import Dashboard from "../components/Dashboard";
import FlashNewsCard from "../components/FlashNewsCard";
import SummaryCard from "../components/SummaryCard";

export default function Home() {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    const handleGenerateSummary = () => {
        console.log("🚀 TODO: Lancer le workflow avec les dates :", startDate, endDate);
    };

    const handleGenerateDailySummary = () => {
        console.log("🚀 TODO: Lancer le workflow pour les dernières 24h");
    };

    const handleGenerateFlashNews = () => {
        console.log("🚀 TODO: Lancer le workflow Flash News");
    };

    return (
        <div className="container mx-auto p-6 space-y-6 max-w-4xl">

            <Dashboard onGenerateDailySummary={handleGenerateDailySummary} />

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
