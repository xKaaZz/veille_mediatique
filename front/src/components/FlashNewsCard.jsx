import React from 'react';
import { Card, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";


export default function FlashNewsCard({ onGenerate }) {
    return (
        <Card>
            <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-semibold">Mode Flash News</h2>
                <Button onClick={onGenerate}>
                    ⚡ Générer le résumé "Flash News"
                </Button>
            </CardContent>
        </Card>
    );
}
