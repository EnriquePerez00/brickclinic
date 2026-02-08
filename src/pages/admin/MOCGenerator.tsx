import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Sparkles, Download, Loader2 } from "lucide-react";
import { toast } from "sonner";

const MOCGenerator = () => {
    const navigate = useNavigate();
    const [partsList, setPartsList] = useState("");
    const [seedPart, setSeedPart] = useState("3001");
    const [numSteps, setNumSteps] = useState(5);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedMOC, setGeneratedMOC] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!partsList.trim()) {
            toast.error("Por favor, ingresa una lista de piezas");
            return;
        }

        setIsGenerating(true);
        setGeneratedMOC(null);

        try {
            // Parse parts list (format: "part_num,quantity" per line)
            const parts = partsList
                .trim()
                .split("\n")
                .map(line => line.trim())
                .filter(line => line.length > 0)
                .map(line => {
                    const [part_num, qty] = line.split(",");
                    return { part_num: part_num?.trim(), quantity: parseInt(qty?.trim() || "1") };
                })
                .filter(p => p.part_num);

            if (parts.length === 0) {
                toast.error("Formato inválido. Usa: part_num,quantity");
                setIsGenerating(false);
                return;
            }

            // Call Edge Function
            const response = await fetch("/api/generate-moc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    parts_inventory: parts,
                    seed_part: seedPart,
                    num_steps: numSteps,
                    theme_id: 158, // Star Wars
                }),
            });

            if (!response.ok) {
                throw new Error("Error generando MOC");
            }

            const data = await response.json();

            if (data.success) {
                setGeneratedMOC(data.ldr_content);
                toast.success("MOC generado exitosamente!");
            } else {
                toast.error(data.error || "Error desconocido");
            }
        } catch (error) {
            console.error(error);
            toast.error("Error al generar MOC. Verifica la consola.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDownload = () => {
        if (!generatedMOC) return;

        const blob = new Blob([generatedMOC], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `moc_starwars_${Date.now()}.ldr`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success("MOC descargado!");
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <header className="max-w-4xl mx-auto mb-8">
                <Link
                    to="/admin/dashboard"
                    className="inline-flex items-center gap-2 text-primary font-medium hover:underline mb-4"
                >
                    <ArrowLeft className="w-4 h-4" /> Volver al Dashboard
                </Link>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                    Generador de MOCs - Star Wars
                </h1>
                <p className="text-gray-500">Genera modelos personalizados usando IA</p>
            </header>

            <main className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Panel */}
                <Card>
                    <CardHeader>
                        <CardTitle>Configuración</CardTitle>
                        <CardDescription>
                            Define el inventario de piezas disponibles y parámetros de generación
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <Label htmlFor="parts-list">
                                Lista de Piezas Disponibles
                                <span className="text-xs text-gray-500 ml-2">
                                    (Formato: part_num,quantity)
                                </span>
                            </Label>
                            <Textarea
                                id="parts-list"
                                placeholder={`3001,10\n3003,5\n3020,8\n3023,12`}
                                value={partsList}
                                onChange={(e) => setPartsList(e.target.value)}
                                className="mt-2 font-mono text-sm h-48"
                            />
                            <p className="text-xs text-gray-400 mt-1">
                                💡 Ejemplo: "3001,10" = 10 unidades de la pieza 3001
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <Label htmlFor="seed-part">Pieza Inicial (Seed)</Label>
                                <Input
                                    id="seed-part"
                                    type="text"
                                    value={seedPart}
                                    onChange={(e) => setSeedPart(e.target.value)}
                                    placeholder="3001"
                                    className="mt-2"
                                />
                            </div>
                            <div>
                                <Label htmlFor="num-steps">Pasos de Generación</Label>
                                <Input
                                    id="num-steps"
                                    type="number"
                                    min="1"
                                    max="20"
                                    value={numSteps}
                                    onChange={(e) => setNumSteps(parseInt(e.target.value))}
                                    className="mt-2"
                                />
                            </div>
                        </div>

                        <Button
                            onClick={handleGenerate}
                            disabled={isGenerating}
                            className="w-full"
                            size="lg"
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Generando...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4 mr-2" />
                                    Generar MOC
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Output Panel */}
                <Card>
                    <CardHeader>
                        <CardTitle>Resultado</CardTitle>
                        <CardDescription>Archivo LDraw generado por la IA</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {!generatedMOC && !isGenerating && (
                            <div className="flex flex-col items-center justify-center h-64 text-center">
                                <Sparkles className="w-12 h-12 text-gray-300 mb-4" />
                                <p className="text-gray-500">
                                    Configura las piezas y genera tu MOC
                                </p>
                            </div>
                        )}

                        {isGenerating && (
                            <div className="flex flex-col items-center justify-center h-64">
                                <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
                                <p className="text-gray-500">Generando MOC...</p>
                                <p className="text-xs text-gray-400 mt-2">
                                    La IA está seleccionando las mejores conexiones
                                </p>
                            </div>
                        )}

                        {generatedMOC && (
                            <div className="space-y-4">
                                <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg max-h-64 overflow-auto">
                                    <pre className="text-xs font-mono text-gray-700 dark:text-gray-300">
                                        {generatedMOC.slice(0, 500)}...
                                    </pre>
                                </div>
                                <Button onClick={handleDownload} className="w-full" variant="outline">
                                    <Download className="w-4 h-4 mr-2" />
                                    Descargar .ldr
                                </Button>
                                <p className="text-xs text-gray-500 text-center">
                                    Abre el archivo en{" "}
                                    <a
                                        href="https://www.bricklink.com/v3/studio/download.page"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-primary hover:underline"
                                    >
                                        BrickLink Studio
                                    </a>{" "}
                                    o LDView
                                </p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </main>
        </div>
    );
};

export default MOCGenerator;
