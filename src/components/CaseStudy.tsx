import { motion } from "framer-motion";
import { TrendingUp, Package, Hammer, Coins, ArrowRight } from "lucide-react";
import { useTranslation, Trans } from "react-i18next";

const CaseStudy = () => {
    const { t } = useTranslation();

    // Data Calculation
    const costs = [
        { label: t('caseStudy.financials.costs.logistics'), value: 20.00 },
        { label: t('caseStudy.financials.costs.hygiene'), value: 79.60 },
        { label: t('caseStudy.financials.costs.recovery'), value: 146.90 }, // 14.90 + 660 * 0.2
        { label: t('caseStudy.financials.costs.sorting'), value: 138.60 }, // 14 blocks * 9.90
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
                        <span className="text-primary font-bold text-sm uppercase tracking-wide">{t('caseStudy.badge')}</span>
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
                        {t('caseStudy.title')}
                    </h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
                        <Trans i18nKey="caseStudy.description" />
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
                            {t('caseStudy.originalMaterial.title')}
                        </h3>

                        <div className="space-y-6">
                            <div className="bg-secondary/30 p-4 rounded-lg">
                                <h4 className="font-semibold text-lg mb-2">{t('caseStudy.originalMaterial.contentTitle')}</h4>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        {t('caseStudy.originalMaterial.items.bigSet')}
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        {t('caseStudy.originalMaterial.items.mediumSets')}
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-primary rounded-full" />
                                        {t('caseStudy.originalMaterial.items.smallSets')}
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-muted-foreground/50 rounded-full" />
                                        {t('caseStudy.originalMaterial.items.random')}
                                    </li>
                                </ul>
                            </div>

                            <div className="bg-secondary/30 p-4 rounded-lg">
                                <h4 className="font-semibold text-lg mb-2">{t('caseStudy.originalMaterial.initialState.title')}</h4>
                                <p className="text-muted-foreground">
                                    <Trans i18nKey="caseStudy.originalMaterial.initialState.description" />
                                </p>
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
                                {t('caseStudy.financials.investmentTitle')}
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
                                    <span>{t('caseStudy.financials.totalCosts')}</span>
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
                                {t('caseStudy.financials.returnTitle')}
                            </h3>

                            <div className="space-y-6 relative z-10">
                                <div>
                                    <span className="block text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">{t('caseStudy.financials.marketValueLabel')}</span>
                                    <div className="text-3xl font-extrabold text-foreground">
                                        {marketValueLow}€ - {marketValueHigh}€
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <ArrowRight className="w-6 h-6 text-muted-foreground rotate-90 lg:rotate-0" />
                                    <div className="bg-background p-4 rounded-lg border border-primary/20 shadow-sm flex-1">
                                        <span className="block text-sm text-primary font-bold mb-1 uppercase tracking-wider">{t('caseStudy.financials.appreciationLabel')}</span>
                                        <div className="text-3xl font-extrabold text-green-600">
                                            +{profitLow.toFixed(0)}€ a +{profitHigh.toFixed(0)}€
                                        </div>

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
