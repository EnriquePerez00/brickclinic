import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Upload } from "lucide-react";
import { toast } from "sonner";

const SimilarSets = () => {
    const navigate = useNavigate();

    useEffect(() => {
        const isAuthenticated = localStorage.getItem("isAdminAuthenticated");
        if (isAuthenticated !== "true") {
            navigate("/admin/login");
        }
    }, [navigate]);

    const handleUpload = () => {
        toast.info("Funcionalidad en desarrollo");
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <div className="max-w-2xl mx-auto">
                <Button variant="ghost" className="mb-6 pl-0 hover:bg-transparent hover:underline" onClick={() => navigate("/admin/dashboard")}>
                    <ArrowLeft className="w-4 h-4 mr-2" /> Volver al Dashboard
                </Button>

                <Card>
                    <CardHeader>
                        <CardTitle>Sets Similares</CardTitle>
                        <CardDescription>
                            Sube un fichero CSV para encontrar sets con inventario compatible.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="text-center py-12 border-dashed border-2 rounded-lg margin-4">
                        <div className="flex flex-col items-center gap-4">
                            <div className="p-4 bg-gray-100 rounded-full">
                                <Upload className="w-8 h-8 text-gray-400" />
                            </div>
                            <div className="space-y-1">
                                <p className="font-medium">Arrastra tu CSV aquí</p>
                                <p className="text-sm text-gray-500">o haz clic para seleccionar</p>
                            </div>
                            <Button onClick={handleUpload} variant="outline">Seleccionar Archivo</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default SimilarSets;
