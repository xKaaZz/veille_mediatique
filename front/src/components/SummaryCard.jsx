import React, { useState } from 'react';
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";

export default function SummaryCard({ startDate, endDate, setStartDate, setEndDate, onGenerate }) {
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleGenerateSummary = () => {
        setMessage("");
        if (!startDate || !endDate) {
            setMessage("❌ Veuillez sélectionner les deux dates.");
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            setMessage("❌ La date de début doit être antérieure à la date de fin.");
            return;
        }

        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
            setMessage("✅ Résumé généré avec succès !");
        }, 2000);
    };

    return (
        <Card className="text-center">
            <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-semibold text-center">Résumé Personnalisé</h2>

                {/* Champs de date */}
                <div className="flex flex-col sm:flex-row gap-4">
                    <input
                        type="date"
                        className="border border-gray-300 p-3 rounded-md w-full"
                        value={startDate || ""}
                        onChange={(e) => setStartDate(e.target.value)}
                    />
                    <input
                        type="date"
                        className="border border-gray-300 p-3 rounded-md w-full"
                        value={endDate || ""}
                        onChange={(e) => setEndDate(e.target.value)}
                    />
                </div>

                <div className="flex justify-center">
                    <Button onClick={handleGenerateSummary} className="w-64">
                        {isLoading ? "⏳ Chargement..." : "➡️ Générer le résumé"}
                    </Button>
                </div>

                {message && (
                    <p className={`message ${message.startsWith("✅") ? "success" : "error"}`}>
                        {message}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
