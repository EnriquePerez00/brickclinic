import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { LogOut, Home, Database, Copy, Sparkles, Download, Loader2, Upload, FileText } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

const Dashboard = () => {
    const navigate = useNavigate();

    // Inventory Generator State
    const [setRef, setSetRef] = useState("");
    const [csvData, setCsvData] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    // Similar Sets State
    const [csvFile, setCsvFile] = useState<File | null>(null);
    const [isComparingSets, setIsComparingSets] = useState(false);
    const [similarSets, setSimilarSets] = useState<any[] | null>(null);
    const [selectedThemes, setSelectedThemes] = useState<string[]>(['Todos']);
    const [filteredSetCount, setFilteredSetCount] = useState<number | null>(null);

    // Fetch filtered set count
    useEffect(() => {
        const fetchCount = async () => {
            // Logic to filter themes for RPC (exclude 'Todos' if others present)
            let rpcThemes: string[] | null = selectedThemes.filter(t => t !== 'Todos');
            if (rpcThemes.length === 0 && selectedThemes.includes('Todos')) rpcThemes = null;

            const { data, error } = await supabase.rpc('get_filtered_set_count', {
                filter_themes: rpcThemes
            });
            if (!error && data !== null) {
                setFilteredSetCount(data);
            }
        };
        fetchCount();
    }, [selectedThemes]);

    // MOC Generator State
    // MOC Generator State
    const [mocFile, setMocFile] = useState<File | null>(null);
    const [mocTheme, setMocTheme] = useState<"Star Wars" | "Technic">("Star Wars");
    const [seedPart, setSeedPart] = useState("3001");
    const [numSteps, setNumSteps] = useState(5);
    const [generatedMOC, setGeneratedMOC] = useState<string | null>(null);
    const [isMOCGenerating, setIsMOCGenerating] = useState(false);

    // Auth check
    useState(() => {
        const isAuthenticated = localStorage.getItem("isAdminAuthenticated");
        if (isAuthenticated !== "true") {
            navigate("/admin/login");
        }
    });

    const handleLogout = () => {
        localStorage.removeItem("isAdminAuthenticated");
        toast.info("Sesión cerrada");
        navigate("/admin/login");
    };

    // === Inventory Generator ===
    const handleGenerateInventory = async () => {
        if (!setRef) {
            toast.error("Ingresa una referencia de set");
            return;
        }

        setIsGenerating(true);
        try {
            const { data, error } = await supabase.functions.invoke("generate-inventory-csv", {
                body: { set_num: setRef },
            });

            if (error) throw error;

            setCsvData(data.csv);
            toast.success("CSV generado exitosamente!");
        } catch (error: any) {
            toast.error(error.message || "Error al generar CSV");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDownloadCSV = () => {
        if (!csvData) return;
        const blob = new Blob([csvData], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `set_${setRef.replace(/[^a-zA-Z0-9]/g, '_')}_inventory.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        toast.success("CSV descargado!");
    };

    // === MOC Generator ===
    // === MOC Generator ===
    const handleGenerateMOC = async () => {
        if (!mocFile) {
            toast.error("Sube un archivo CSV de piezas");
            return;
        }

        setIsMOCGenerating(true);
        setGeneratedMOC(null);

        try {
            // Parse CSV on client
            const text = await mocFile.text();
            const lines = text.split('\n');
            const partsPool = [];

            // Heuristic: Check first line for headers
            let startIdx = 0;
            const headers = lines[0].toLowerCase().split(',').map(h => h.trim());

            let pIdx = headers.indexOf('part_num');
            let cIdx = headers.indexOf('color_id');

            if (pIdx === -1) pIdx = 0; // Default pos 0
            if (cIdx === -1) cIdx = 1; // Default pos 1

            for (let i = startIdx; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                const cols = line.split(',').map(c => c.trim().replace(/"/g, ''));

                // Skip header line if it looks like a header
                if (cols[pIdx] === 'part_num' || cols[pIdx] === 'Part Num') continue;

                if (cols.length >= 2) {
                    partsPool.push({
                        part_num: cols[pIdx],
                        color_id: parseInt(cols[cIdx]) || -1,
                        qty: 1
                    });
                }
            }

            if (partsPool.length === 0) throw new Error("No se encontraron piezas en el CSV");

            const { data, error } = await supabase.functions.invoke("generate-moc", {
                body: {
                    parts_pool: partsPool,
                    theme_name: mocTheme,
                    max_parts: numSteps * 5 // 5 parts per step
                },
            });

            if (error) throw error;

            if (data.success) {
                setGeneratedMOC(data.ldr_content);
                toast.success(`MOC de ${mocTheme} generado con ${partsPool.length} piezas disponibles!`);
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
        } catch (error: any) {
            console.error(error);
            toast.error(error.message || "Error al generar MOC");
        } finally {
            setIsMOCGenerating(false);
        }
    };

    const handleDownloadMissingParts = async (setNum: string) => {
        if (!csvFile) {
            toast.error("No hay archivo CSV cargado. Por favor sube tu inventario primero.");
            return;
        }

        try {
            toast.info(`Calculando faltantes para ${setNum}...`);
            const text = await csvFile.text();

            // Basic CSV Parse (Matches backend logic)
            const lines = text.split(/\r?\n/);
            if (lines.length < 2) throw new Error("CSV vacío o inválido");

            const header = lines[0].toLowerCase();
            const sep = header.includes(';') ? ';' : ',';
            const headers = header.split(sep).map(h => h.trim().replace(/"/g, ''));

            const partNumIdx = headers.findIndex(h => h.includes('part') && h.includes('num'));
            const colorIdIdx = headers.findIndex(h => h.includes('color') && (h.includes('id') || h.includes('name') === false)); // prioritizing ID logic
            // Fallback for color if specialized logic needed, but backend uses parseInt so expects ID column
            const quantityIdx = headers.findIndex(h => h.includes('qty') || h.includes('quantity'));

            if (partNumIdx === -1) throw new Error("No se encontró columna 'part_num' en el CSV");

            const userParts = lines.slice(1)
                .map(line => {
                    if (!line.trim()) return null;
                    const parts = line.split(sep);

                    // Parse color_id correctly (0 is valid - Black color!)
                    const colorIdParsed = colorIdIdx !== -1 ? parseInt(parts[colorIdIdx]) : NaN;
                    const quantityParsed = quantityIdx !== -1 ? parseInt(parts[quantityIdx]) : NaN;

                    return {
                        part_num: parts[partNumIdx]?.trim(),
                        color_id: !isNaN(colorIdParsed) ? colorIdParsed : -1,
                        quantity: !isNaN(quantityParsed) && quantityParsed > 0 ? quantityParsed : 1
                    };
                })
                .filter(p => p && p.part_num);

            const { data, error } = await supabase.rpc('get_set_missing_parts', {
                p_set_num: setNum,
                user_parts: userParts
            });

            if (error) throw error;

            if (!data || data.length === 0) {
                toast.success("¡Felicidades! Tienes todas las piezas.");
                return;
            }

            // Generate "piezas_pdtes" CSV
            const csvRows = [
                "part_num,color_id,quantity,part_name,color_name"
            ];

            data.forEach((row: any) => {
                csvRows.push(`${row.part_num},${row.color_id},${row.missing_qty},"${(row.part_name || '').replace(/"/g, '""')}","${(row.color_name || '').replace(/"/g, '""')}"`);
            });

            const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `set_${setNum}_piezas_pdtes.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            toast.success(`Descargado: set_${setNum}_piezas_pdtes.csv (Faltan ${data.length} tipos de piezas)`);

        } catch (error: any) {
            console.error("Error missing parts:", error);
            toast.error("Error al calcular faltantes: " + error.message);
        }
    };

    const handleDownloadMOC = () => {
        if (!generatedMOC) return;
        const blob = new Blob([generatedMOC], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `moc_${mocTheme.replace(/\s/g, '_').toLowerCase()}_${Date.now()}.ldr`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        toast.success("MOC descargado!");
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <header className="max-w-7xl mx-auto flex justify-between items-center mb-8">
                <div>
                    <Link to="/" className="flex items-center gap-2 text-primary font-bold hover:underline mb-1">
                        <Home className="w-4 h-4" /> Ir a la web
                    </Link>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Panel de Control</h1>
                    <p className="text-gray-500">Herramientas de administración de Brickclinic</p>
                </div>
                <Button variant="outline" onClick={handleLogout} className="flex gap-2">
                    <LogOut className="w-4 h-4" /> Salir
                </Button>
            </header>

            <main className="max-w-7xl mx-auto">
                <Tabs defaultValue="inventory" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="inventory" className="flex gap-2">
                            <Database className="w-4 h-4" />
                            Generador Inventario
                        </TabsTrigger>
                        <TabsTrigger value="similar" className="flex gap-2">
                            <Copy className="w-4 h-4" />
                            Sets Similares
                        </TabsTrigger>
                        <TabsTrigger value="moc" className="flex gap-2">
                            <Sparkles className="w-4 h-4" />
                            Generador MOCs
                        </TabsTrigger>
                    </TabsList>

                    {/* === TAB 1: Inventory Generator === */}
                    <TabsContent value="inventory">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Entrada</CardTitle>
                                    <CardDescription>Referencia del set LEGO (ej. 75051-1)</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <Label htmlFor="set-ref">Referencia del Set</Label>
                                        <Input
                                            id="set-ref"
                                            placeholder="75051-1"
                                            value={setRef}
                                            onChange={(e) => setSetRef(e.target.value)}
                                            className="mt-2"
                                        />
                                    </div>
                                    <Button onClick={handleGenerateInventory} disabled={isGenerating} className="w-full">
                                        {isGenerating ? (
                                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Generando...</>
                                        ) : (
                                            <><Database className="w-4 h-4 mr-2" />Generar CSV</>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Resultado</CardTitle>
                                    <CardDescription>CSV con inventario de piezas</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    {csvData ? (
                                        <div className="space-y-4">
                                            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg max-h-64 overflow-auto">
                                                <pre className="text-xs font-mono">{csvData.slice(0, 300)}...</pre>
                                            </div>
                                            <Button onClick={handleDownloadCSV} className="w-full" variant="outline">
                                                <Download className="w-4 h-4 mr-2" />Descargar CSV
                                            </Button>
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 text-center py-8">Genera un CSV para ver el resultado</p>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    {/* === TAB 2: Similar Sets === */}
                    <TabsContent value="similar">
                        <Card className="mt-6">
                            <CardHeader>
                                <CardTitle>Comparador de Sets</CardTitle>
                                <CardDescription>Carga un CSV de inventario para encontrar sets similares</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-6">
                                    {/* Theme Filter */}
                                    <div className="mb-6">
                                        <div className="flex justify-between items-center mb-2">
                                            <Label className="block">Filtrar por Temática</Label>
                                            {filteredSetCount !== null && (
                                                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                                    sets a mapear: {filteredSetCount}
                                                </span>
                                            )}
                                        </div>
                                        <div className="flex flex-wrap gap-4">
                                            {['Todos', 'Star Wars', 'Technic', 'City', 'Architecture', 'Ninjago', 'Otros'].map((theme) => (
                                                <div key={theme} className="flex items-center space-x-2">
                                                    <input
                                                        type="checkbox"
                                                        id={`theme-${theme}`}
                                                        value={theme}
                                                        disabled={isComparingSets}
                                                        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
                                                        checked={selectedThemes.includes(theme)}
                                                        onChange={(e) => {
                                                            const isChecked = e.target.checked;
                                                            let newThemes = [...selectedThemes];

                                                            if (theme === 'Todos') {
                                                                if (isChecked) newThemes = ['Todos'];
                                                                else newThemes = []; // Prevent empty? Maybe default to Todos on backend
                                                            } else {
                                                                if (isChecked) {
                                                                    newThemes = newThemes.filter(t => t !== 'Todos');
                                                                    newThemes.push(theme);
                                                                } else {
                                                                    newThemes = newThemes.filter(t => t !== theme);
                                                                }
                                                                if (newThemes.length === 0) newThemes = ['Todos'];
                                                            }
                                                            setSelectedThemes(newThemes);
                                                        }}
                                                    />
                                                    <label htmlFor={`theme-${theme}`} className="text-sm font-medium leading-none cursor-pointer">
                                                        {theme}
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Upload Section */}
                                    <div className="border-2 border-dashed rounded-lg p-6 text-center">
                                        <Upload className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                        <Label htmlFor="csv-upload" className="cursor-pointer">
                                            <span className="text-blue-600 hover:text-blue-700">Selecciona un archivo CSV</span>
                                            <span className="text-gray-500"> o arrástralo aquí</span>
                                        </Label>
                                        <Input
                                            id="csv-upload"
                                            type="file"
                                            accept=".csv"
                                            className="hidden"
                                            onChange={(e) => {
                                                const file = e.target.files?.[0];
                                                if (file) {
                                                    setIsComparingSets(true);
                                                    setCsvFile(file); // Store file for later use
                                                    setSimilarSets(null);

                                                    const processUpload = async () => {
                                                        try {
                                                            const formData = new FormData();
                                                            formData.append('file', file);

                                                            // Collect Themes from State
                                                            const rpcThemes = selectedThemes.filter(t => t !== 'Todos');
                                                            if (rpcThemes.length > 0) {
                                                                formData.append('themes', rpcThemes.join(','));
                                                            }

                                                            const { data: { session } } = await supabase.auth.getSession();

                                                            const response = await fetch(
                                                                `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/compare-sets`,
                                                                {
                                                                    method: 'POST',
                                                                    headers: {
                                                                        'Authorization': `Bearer ${session?.access_token || import.meta.env.VITE_SUPABASE_ANON_KEY}`,
                                                                        // FormData automatically sets Content-Type
                                                                    },
                                                                    body: formData
                                                                }
                                                            );

                                                            if (!response.ok) throw new Error('Error de conexión con el servidor');
                                                            if (!response.body) throw new Error('No se recibió respuesta del servidor');

                                                            const reader = response.body.getReader();
                                                            const decoder = new TextDecoder();
                                                            let buffer = '';

                                                            while (true) {
                                                                const { done, value } = await reader.read();
                                                                if (done) break;

                                                                buffer += decoder.decode(value, { stream: true });
                                                                const lines = buffer.split('\n');
                                                                buffer = lines.pop() || ''; // Keep incomplete line in buffer

                                                                for (const line of lines) {
                                                                    if (!line.trim()) continue;
                                                                    try {
                                                                        const msg = JSON.parse(line);
                                                                        if (msg.type === 'batch') {
                                                                            setSimilarSets(prev => {
                                                                                const newSet = [...(prev || []), ...msg.data];
                                                                                return newSet
                                                                                    .filter((s: any) => (parseInt(s.total_parts || s.num_parts || '0')) >= 20) // Filter out small sets (< 20 parts)
                                                                                    .sort((a: any, b: any) => {
                                                                                        const valA = parseFloat(a.match_percent || a.similarity || '0');
                                                                                        const valB = parseFloat(b.match_percent || b.similarity || '0');
                                                                                        return valB - valA;
                                                                                    }).slice(0, 1000); // Allow large pool for filtering
                                                                            });
                                                                        } else if (msg.type === 'metadata') {
                                                                            toast.info(`Analizando ${msg.total} sets candidatos...`);
                                                                        } else if (msg.type === 'error') {
                                                                            toast.error(`Error en stream: ${msg.message}`);
                                                                        } else if (msg.type === 'debug') {
                                                                            console.log('DEBUG SERVER:', msg.data);
                                                                        }
                                                                    } catch (e) {
                                                                        console.warn('Error parsing JSON chunk', e);
                                                                    }
                                                                }
                                                            }

                                                            toast.success(`Análisis completo!`);
                                                            setIsComparingSets(false);
                                                        } catch (error: any) {
                                                            console.error('Full error:', error);
                                                            toast.error(error.message || "Error al comparar sets");
                                                        } finally {
                                                            setIsComparingSets(false);
                                                        }
                                                    };
                                                    processUpload();
                                                }
                                            }}
                                        />
                                        <p className="text-xs text-gray-400 mt-2">
                                            Formato: part_num,color_id,quantity
                                        </p>


                                    </div>

                                    {/* Loading State */}
                                    {isComparingSets && (
                                        <div className="flex items-center justify-center py-8">
                                            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                                            <span className="ml-3 text-gray-600">Comparando con 25,000+ sets...</span>
                                        </div>
                                    )}

                                    {/* Results Table */}
                                    {similarSets && similarSets.length > 0 && (
                                        <div className="space-y-12">
                                            {[
                                                { label: "Sets Grandes (> 1000 piezas)", filter: (s: any) => (parseInt(s.total_parts || s.num_parts || 0)) > 1000 },
                                                { label: "Sets Medianos (500 - 1000 piezas)", filter: (s: any) => (parseInt(s.total_parts || s.num_parts || 0)) >= 500 && (parseInt(s.total_parts || s.num_parts || 0)) <= 1000 },
                                                { label: "Sets Pequeños (200 - 500 piezas)", filter: (s: any) => (parseInt(s.total_parts || s.num_parts || 0)) >= 200 && (parseInt(s.total_parts || s.num_parts || 0)) < 500 },
                                                { label: "Mini Sets (< 200 piezas)", filter: (s: any) => (parseInt(s.total_parts || s.num_parts || 0)) < 200 }
                                            ].map((category, catIndex) => {
                                                const categorySets = similarSets
                                                    .filter(category.filter)
                                                    .sort((a: any, b: any) => {
                                                        const valA = parseFloat(a.match_percent || a.similarity || '0');
                                                        const valB = parseFloat(b.match_percent || b.similarity || '0');
                                                        return valB - valA;
                                                    })
                                                    .slice(0, 5);

                                                if (categorySets.length === 0) return null;

                                                return (
                                                    <div key={catIndex} className="space-y-4">
                                                        <h3 className="font-bold text-xl text-gray-800 border-l-4 border-blue-600 pl-3">{category.label}</h3>
                                                        <div className="overflow-x-auto shadow-sm rounded-lg border border-gray-200">
                                                            <table className="w-full border-collapse bg-white">
                                                                <thead className="bg-gray-50 border-b border-gray-200">
                                                                    <tr>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Ranking</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Set</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Nombre</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Año</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Piezas (Total)</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider">Piezas (Dif)</th>
                                                                        <th className="text-left p-4 font-semibold text-gray-600 uppercase text-xs tracking-wider w-1/4">Similaridad</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody className="divide-y divide-gray-100">
                                                                    {categorySets.map((set: any, index: number) => (
                                                                        <tr key={`${set.set_num}-${index}`} className="hover:bg-blue-50/40 transition-colors">
                                                                            <td className="p-4">
                                                                                <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm shadow-sm ${index === 0 ? 'bg-yellow-100 text-yellow-700 ring-1 ring-yellow-200' :
                                                                                    index === 1 ? 'bg-gray-100 text-gray-700 ring-1 ring-gray-200' :
                                                                                        index === 2 ? 'bg-orange-100 text-orange-700 ring-1 ring-orange-200' :
                                                                                            'bg-blue-50 text-blue-600 ring-1 ring-blue-100'
                                                                                    }`}>
                                                                                    {index + 1}
                                                                                </span>
                                                                            </td>
                                                                            <td className="p-4 font-mono text-sm text-gray-600 font-medium">{set.set_num}</td>
                                                                            <td className="p-4 font-medium text-gray-800">{set.name}</td>
                                                                            <td className="p-4 text-gray-500">{set.year}</td>
                                                                            <td className="p-4 text-gray-700 font-mono font-medium">{set.total_parts || set.num_parts}</td>
                                                                            <td className="p-4 text-gray-700 font-mono font-medium">{set.missing_pieces !== undefined ? set.missing_pieces : '-'}</td>
                                                                            <td className="p-4">
                                                                                <div className="flex items-center gap-3">
                                                                                    <div className="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden ring-1 ring-gray-200/50">
                                                                                        <div
                                                                                            className={`h-full rounded-full transition-all duration-500 shadow-sm ${(parseFloat(set.match_percent || set.similarity || '0') < 30) ? 'bg-red-500' :
                                                                                                (parseFloat(set.match_percent || set.similarity || '0') < 70) ? 'bg-yellow-500' :
                                                                                                    'bg-green-500'
                                                                                                }`}
                                                                                            style={{ width: `${Math.min(100, Math.max(5, parseFloat(set.match_percent || set.similarity || '0')))}%` }}
                                                                                        />
                                                                                    </div>
                                                                                    <span className={`font-bold text-sm min-w-[3.5rem] text-right ${(parseFloat(set.match_percent || set.similarity || '0') < 30) ? 'text-red-600' :
                                                                                        (parseFloat(set.match_percent || set.similarity || '0') < 70) ? 'text-yellow-600' :
                                                                                            'text-green-600'
                                                                                        }`}>{set.match_percent || set.similarity}%</span>
                                                                                    <button
                                                                                        className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-blue-600 transition-colors ml-2"
                                                                                        title="Descargar piezas faltantes (CSV)"
                                                                                        onClick={() => handleDownloadMissingParts(set.set_num)}
                                                                                    >
                                                                                        <FileText className="w-4 h-4" />
                                                                                    </button>
                                                                                </div>
                                                                            </td>
                                                                        </tr>
                                                                    ))}
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}

                                    {/* Empty State */}
                                    {!isComparingSets && !similarSets && (
                                        <div className="flex flex-col items-center justify-center py-8 text-center text-gray-500">
                                            <Copy className="w-16 h-16 text-gray-300 mb-4" />
                                            <p>Sube un CSV para comenzar el análisis</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* === TAB 3: MOC Generator === */}
                    <TabsContent value="moc">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Configuración</CardTitle>
                                    <CardDescription>Parámetros de generación DNA-aware</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {/* MOC Theme Selector */}
                                    <div>
                                        <Label className="block mb-2">Serie Lego</Label>
                                        <div className="flex gap-4">
                                            <div className="flex items-center space-x-2">
                                                <input
                                                    type="radio"
                                                    id="moc-sw"
                                                    value="Star Wars"
                                                    checked={mocTheme === "Star Wars"}
                                                    onChange={() => setMocTheme("Star Wars")}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                                                />
                                                <Label htmlFor="moc-sw" className="font-medium">Star Wars</Label>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <input
                                                    type="radio"
                                                    id="moc-technic"
                                                    value="Technic"
                                                    checked={mocTheme === "Technic"}
                                                    onChange={() => setMocTheme("Technic")}
                                                    className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                                                />
                                                <Label htmlFor="moc-technic" className="font-medium">Technic</Label>
                                            </div>
                                        </div>
                                    </div>

                                    {/* CSV Upload for MOC */}
                                    <div className="border-2 border-dashed rounded-lg p-6 text-center">
                                        <Upload className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                                        <Label htmlFor="moc-file-upload" className="cursor-pointer">
                                            <span className="text-blue-600 hover:text-blue-700 font-medium">Sube inventario .csv</span>
                                        </Label>
                                        <Input
                                            id="moc-file-upload"
                                            type="file"
                                            accept=".csv"
                                            className="hidden"
                                            onChange={(e) => setMocFile(e.target.files?.[0] || null)}
                                        />
                                        {mocFile && (
                                            <p className="text-sm text-green-600 mt-2 font-mono">
                                                {mocFile.name} ({(mocFile.size / 1024).toFixed(1)} KB)
                                            </p>
                                        )}
                                        <p className="text-xs text-gray-400 mt-1">Columns: part_num, color_id, qty</p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label htmlFor="seed">Pieza Inicial</Label>
                                            <Input
                                                id="seed"
                                                value={seedPart}
                                                onChange={(e) => setSeedPart(e.target.value)}
                                                className="mt-2"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="steps">Pasos (x5 piezas)</Label>
                                            <Input
                                                id="steps"
                                                type="number"
                                                min="1"
                                                max="20"
                                                value={numSteps}
                                                onChange={(e) => setNumSteps(parseInt(e.target.value))}
                                                className="mt-2"
                                            />
                                        </div>
                                    </div>
                                    <Button onClick={handleGenerateMOC} disabled={isMOCGenerating} className="w-full">
                                        {isMOCGenerating ? (
                                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Generando...</>
                                        ) : (
                                            <><Sparkles className="w-4 h-4 mr-2" />Generar MOC (DNA + Physics)</>
                                        )}
                                    </Button>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Resultado</CardTitle>
                                    <CardDescription>MOC generado con DNA Star Wars</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    {generatedMOC ? (
                                        <div className="space-y-4">
                                            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg max-h-64 overflow-auto">
                                                <pre className="text-xs font-mono">{generatedMOC.slice(0, 300)}...</pre>
                                            </div>
                                            <Button onClick={handleDownloadMOC} className="w-full" variant="outline">
                                                <Download className="w-4 h-4 mr-2" />Descargar .ldr
                                            </Button>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center h-48 text-center">
                                            <Sparkles className="w-12 h-12 text-gray-300 mb-4" />
                                            <p className="text-gray-500">Genera tu MOC</p>
                                            <p className="text-xs text-gray-400 mt-2">
                                                DNA-conditioned · Physics-validated
                                            </p>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>
                </Tabs>
            </main>
        </div>
    );
};

export default Dashboard;
