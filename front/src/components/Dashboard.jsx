import React from 'react';
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";

export default function Dashboard({ onGenerateDailySummary }) {
    return (
        <div className="p-6 space-y-6">
            <Card>
                <CardContent className="p-4 space-y-4">
                    <h2 className="text-xl font-semibold">Résumé Quotidien</h2>
                    <Button onClick={onGenerateDailySummary}>
                        ➡️ Générer le résumé des dernières 24h
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
