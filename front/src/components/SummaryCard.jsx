import React, { useState } from 'react';
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";
import { DatePicker } from "./ui/DatePicker";

export default function SummaryCard({ startDate, endDate, setStartDate, setEndDate, onGenerate }) {
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleGenerateSummary = () => {
        setMessage(""); // Réinitialise le message
        if (!startDate || !endDate) {
            setMessage("❌ Veuillez sélectionner les deux dates.");
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            setMessage("❌ La date de début doit être antérieure à la date de fin.");
            return;
        }

        if (new Date(startDate) > new Date()) {
            setMessage("❌ La date de début ne peut pas être dans le futur.");
            return;
        }

        setIsLoading(true); // Démarrage du spinner
        setTimeout(() => {
            setIsLoading(false); // Fin du spinner
            setMessage("✅ Résumé généré avec succès !");
        }, 2000);
    };

    return (
        <Card>
            <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-semibold">Résumé Personnalisé</h2>
                <div className="flex gap-4">
                    <DatePicker 
                        placeholder="Date de début" 
                        value={startDate} 
                        onChange={setStartDate} 
                    />
                    <DatePicker 
                        placeholder="Date de fin" 
                        value={endDate} 
                        onChange={setEndDate} 
                    />
                </div>

                <Button onClick={handleGenerateSummary} disabled={isLoading}>
                    {isLoading ? "⏳ Chargement..." : "➡️ Générer le résumé"}
                </Button>

                {message && (
                    <p className={`text-sm mt-2 ${message.startsWith("✅") ? "text-green-600" : "text-red-600"}`}>
                        {message}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
