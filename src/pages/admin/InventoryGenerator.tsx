import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

const InventoryGenerator = () => {
    const navigate = useNavigate();
    const [setId, setSetId] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const isAuthenticated = localStorage.getItem("isAdminAuthenticated");
        if (isAuthenticated !== "true") {
            navigate("/admin/login");
        }
    }, [navigate]);

    const generateInventory = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!setId.trim()) return;

        setLoading(true);
        try {
            // 1. Get Inventory ID from Set ID
            // Using 'parts' table joining logic might be complex with simple client query, 
            // but let's try direct joins if foreign keys allow, or strictly following schema.
            // Based on schema: inventory_parts links inventory_id -> part_num. 
            // inventories links set_num.

            console.log(`Searching for set: ${setId}`);

            const { data: inventoryData, error: invError } = await supabase
                .from("inventories")
                .select("id, version")
                .eq("set_num", setId)
                .order("version", { ascending: false }) // Get latest version usually?
                .limit(1)
                .single();

            if (invError || !inventoryData) {
                throw new Error(`Set no encontrado: ${setId} (Error: ${invError?.message})`);
            }

            console.log("Inventory found:", inventoryData);
            const inventoryId = inventoryData.id;

            // 2. Get Parts for this inventory
            // We need to join with 'parts' to get name, and 'colors' maybe?
            // Supabase JS client allows deep selecting if relations exist.
            // Let's fetch raw first.

            const { data: partsData, error: partsError } = await supabase
                .from("inventory_parts")
                .select(`
          quantity,
          is_spare,
          part_num,
          color_id,
          parts (name),
          colors (name, rgb)
        `)
                .eq("inventory_id", inventoryId);

            if (partsError) {
                throw new Error(`Error recuperando piezas: ${partsError.message}`);
            }

            if (!partsData || partsData.length === 0) {
                toast.warning("El set existe pero no tiene piezas registradas.");
                setLoading(false);
                return;
            }

            // 3. Generate CSV
            const csvHeader = "Part Num,Quantity,Part Name,Color,Is Spare\n";
            const csvRows = partsData.map(item => {
                // Safe access to joined data (it comes as array or object depending on relation, usually object for foreign key)
                // @ts-ignore
                const partName = item.parts?.name ? `"${item.parts.name.replace(/"/g, '""')}"` : "Desconocido";
                // @ts-ignore
                const colorName = item.colors?.name || "Desconocido";

                return `${item.part_num},${item.quantity},${partName},${colorName},${item.is_spare}`;
            });

            const csvContent = csvHeader + csvRows.join("\n");

            // 4. Download
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", `inventario_piezas_${setId}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            toast.success(`Inventario descargado: ${partsData.length} líneas`);

        } catch (error: any) {
            console.error(error);
            toast.error(error.message || "Error generando inventario");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <div className="max-w-2xl mx-auto">
                <Button variant="ghost" className="mb-6 pl-0 hover:bg-transparent hover:underline" onClick={() => navigate("/admin/dashboard")}>
                    <ArrowLeft className="w-4 h-4 mr-2" /> Volver al Dashboard
                </Button>

                <Card>
                    <CardHeader>
                        <CardTitle>Generador de Inventario</CardTitle>
                        <CardDescription>
                            Introduce la referencia del set (ej. 75051-1) para descargar su listado de piezas.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={generateInventory} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Referencia LEGO</label>
                                <Input
                                    placeholder="Ej: 75051-1"
                                    value={setId}
                                    onChange={(e) => setSetId(e.target.value)}
                                    disabled={loading}
                                />
                            </div>

                            <Button type="submit" className="w-full" disabled={loading}>
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Procesando...
                                    </>
                                ) : (
                                    <>
                                        <Download className="w-4 h-4 mr-2" /> Generar CSV
                                    </>
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default InventoryGenerator;
