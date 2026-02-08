import { motion } from "framer-motion";
import { TrendingUp, Package, Hammer, Coins, ArrowRight } from "lucide-react";

const CaseStudy = () => {
    // Data Calculation
    const costs = [
        { label: "Logística (Envíos)", value: 20.00 },
        { label: "Higienización y Análisis (8kg)", value: 79.60 },
        { label: "Recuperación (Sets)", value: 146.90 }, // 14.90 + 660 * 0.2
        { label: "Clasificación y Devolución", value: 138.60 }, // 14 blocks * 9.90
    ];

    const totalCost = costs.reduce((acc, curr) => acc + curr.value, 0);
    const marketValueLow = 550;
    const marketValueHigh = 850;
    const profitLow = marketValueLow - totalCost;
    const profitHigh = marketValueHigh - totalCost;

    return (
        <section id="ejemplo-valor" className="py-24 bg-background">
            <div className="container mx-auto px-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <div className="inline-flex items-center justify-center p-2 bg-primary/10 rounded-full mb-4">
                        <TrendingUp className="w-6 h-6 text-primary mr-2" />
                        <span className="text-primary font-bold text-sm uppercase tracking-wide">Caso de Éxito Real</span>
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
                        Ejemplo de Puesta en Valor
                    </h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
                        Analizamos la rentabilidad de restaurar una <strong>cubeta de 8kg de LEGO Technic</strong>.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">

                    {/* LEFT COLUMN: The Input (The Bucket) */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="bg-card border border-border rounded-xl p-8 shadow-sm"
                    >
                        <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                            <Package className="w-6 h-6 text-primary" />
                            El Material Recibido
                        </h3>

                        <div className="space-y-6">
                            <div className="bg-secondary/30 p-4 rounded-lg">
                                <h4 className="font-semibold text-lg mb-2">Contenido (8 kg Total)</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        1 Set Grande (2500 - 4000 piezas)
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        3 Sets Medianos (500 - 1500 piezas)
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        2 Sets Pequeños (100 - 400 piezas)
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-muted-foreground/50 rounded-full" />
                                        ~20% Piezas "Random" (Sueltas)
                                    </li>
                                </ul>
                            </div>

                            <div className="bg-secondary/30 p-4 rounded-lg">
                                <h4 className="font-semibold text-lg mb-2">Estado Inicial</h4>
                                <p className="text-muted-foreground">Sets parcialmente desmantelados. Estimamos un <strong>10% de piezas perdidas</strong> que necesitamos reponer.</p>
                            </div>
                        </div>
                    </motion.div>

                    {/* RIGHT COLUMN: The Financial Breakdown */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="space-y-8"
                    >
                        {/* Costs Breakdown */}
                        <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <Hammer className="w-5 h-5 text-muted-foreground" />
                                Inversión Necesaria
                            </h3>
                            <div className="space-y-3">
                                {costs.map((cost, idx) => (
                                    <div key={idx} className="flex justify-between items-center text-sm">
                                        <span className="text-muted-foreground">{cost.label}</span>
                                        <span className="font-mono font-medium">{cost.value.toFixed(2)}€</span>
                                    </div>
                                ))}
                                <div className="h-px bg-border my-2" />
                                <div className="flex justify-between items-center text-lg font-bold">
                                    <span>Total Costes</span>
                                    <span className="text-destructive font-mono">{totalCost.toFixed(2)}€</span>
                                </div>
                            </div>
                        </div>

                        {/* Value & Profit */}
                        <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 shadow-md relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-4 opacity-5">
                                <Coins className="w-32 h-32" />
                            </div>

                            <h3 className="text-2xl font-bold mb-6 flex items-center gap-2 text-foreground relative z-10">
                                <Coins className="w-6 h-6 text-primary" />
                                Gastos vs Retorno
                            </h3>

                            <div className="space-y-6 relative z-10">
                                <div>
                                    <span className="block text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Valor de Mercado (Sets Nuevos)</span>
                                    <div className="text-3xl font-extrabold text-foreground">
                                        {marketValueLow}€ - {marketValueHigh}€
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <ArrowRight className="w-6 h-6 text-muted-foreground rotate-90 lg:rotate-0" />
                                    <div className="bg-background p-4 rounded-lg border border-primary/20 shadow-sm flex-1">
                                        <span className="block text-sm text-primary font-bold mb-1 uppercase tracking-wider">Revalorización de la "pila Lego"</span>
                                        <div className="text-3xl font-extrabold text-green-600">
                                            +{profitLow.toFixed(0)}€ a +{profitHigh.toFixed(0)}€
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            Revalorización neta desde que nos los envias hasta que los recuperas.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default CaseStudy;
