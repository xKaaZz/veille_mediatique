import React from 'react';
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";

export default function FlashNewsCard({ onGenerate }) {
    return (
        <Card className="text-center">
            <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-semibold text-center">Mode Flash News</h2>
                <div className="flex justify-center">
                    <Button onClick={onGenerate} className="w-64">
                        ⚡ Générer le résumé "Flash News"
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
