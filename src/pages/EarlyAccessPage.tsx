import { useState } from "react";
import { useTranslation } from "react-i18next";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { ChevronRight, Check, History, Layers, Puzzle, TrendingUp, ArrowRight, Scale, Package, Plus } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import Navbar from "@/components/Navbar";

// Popular Themes (Mostly proper names, keeping them static outside or inside if we want to translate some)
const POPULAR_THEMES = [
    "Star Wars™", "LEGO® Technic", "LEGO® City", "Harry Potter™",
    "LEGO® Ninjago", "Marvel™ / DC™", "LEGO® Icons / Creator Expert",
    "LEGO® Friends", "LEGO® Speed Champions", "LEGO® Classic / Creator"
];

export default function EarlyAccessPage() {
    const { t } = useTranslation();
    const [step, setStep] = useState(1);
    const [answers, setAnswers] = useState<{
        question_1: string[];
        question_2: string;
        question_3: string[]; // Series
        otherSeries: string;
        email: string;
        estimationType: "weight" | "sets" | null;
        weightValue: number;
    }>({
        question_1: [],
        question_2: "",
        question_3: [],
        otherSeries: "",
        email: "",
        estimationType: null,
        weightValue: 0,
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [inputOtherOpen, setInputOtherOpen] = useState(false);
    const { toast } = useToast();

    // Move options inside component to use translations
    const AUDIENCE_OPTIONS = [
        { id: "recover", label: t('earlyAccess.steps.1.options.recover'), icon: History },
        { id: "sort", label: t('earlyAccess.steps.1.options.sort'), icon: Layers },
        { id: "complete", label: t('earlyAccess.steps.1.options.complete'), icon: Puzzle },
        { id: "invest", label: t('earlyAccess.steps.1.options.invest'), icon: TrendingUp },
    ];

    const OWNERSHIP_OPTIONS = [
        { id: "0-5", label: t('earlyAccess.steps.2.setsOptions.0-5') },
        { id: "6-20", label: t('earlyAccess.steps.2.setsOptions.6-20') },
        { id: "21-50", label: t('earlyAccess.steps.2.setsOptions.21-50') },
        { id: "50+", label: t('earlyAccess.steps.2.setsOptions.50+') },
    ];

    const handleOptionSelect = (key: "question_1" | "question_2" | "question_3", value: string) => {
        setAnswers((prev) => {
            if (key === "question_1" || key === "question_3") {
                const current = prev[key];
                // Toggle selection
                const newSelection = current.includes(value)
                    ? current.filter((id) => id !== value)
                    : [...current, value];
                return { ...prev, [key]: newSelection };
            } else {
                return { ...prev, [key]: value };
            }
        });

        // specific auto-advance for question 2 ONLY if it is NOT the weight slider (sets buttons directly advance)
        if (key === "question_2" && answers.estimationType === "sets") {
            setTimeout(() => setStep((prev) => prev + 1), 300);
        }
    };

    const handleEstimationTypeSelect = (type: "weight" | "sets") => {
        setAnswers(prev => ({ ...prev, estimationType: type }));
    };

    const handleWeightChange = (value: number[]) => {
        setAnswers(prev => ({
            ...prev,
            weightValue: value[0],
            question_2: value[0] >= 50 ? "+50 kg" : `${value[0]} kg`
        }));
    };

    const confirmWeightSelection = () => {
        setStep(prev => prev + 1);
    };

    const handleNextStep = () => {
        if (step === 1 && answers.question_1.length === 0) {
            toast({
                title: t('earlyAccess.toast.selectOption'),
                variant: "destructive",
            });
            return;
        }
        setStep((prev) => prev + 1);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!answers.email) return;

        setIsSubmitting(true);
        try {
            // Map state keys to DB column names (lowercase)
            const payload = {
                question_1: JSON.stringify(answers.question_1),
                question_2: answers.question_2,
                question_3: JSON.stringify(answers.question_3),
                otherseries: answers.otherSeries,
                estimationtype: answers.estimationType,
                weightvalue: answers.weightValue,
                email: answers.email
            };

            const { error } = await supabase
                .from("early_access_responses")
                .insert([payload]);

            if (error) throw error;

            setIsSuccess(true);
            toast({
                title: t('earlyAccess.toast.successTitle'),
                description: t('earlyAccess.toast.successDesc'),
            });
        } catch (error: any) {
            console.error("Error submitting form:", error);
            toast({
                title: t('earlyAccess.toast.errorTitle'),
                description: t('earlyAccess.toast.errorDesc', { message: error.message || "Inténtalo de nuevo." }),
                variant: "destructive",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const containerVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
        exit: { opacity: 0, x: -20, transition: { duration: 0.3 } },
    };

    if (isSuccess) {
        return (
            <div className="min-h-screen bg-background flex flex-col">
                <Navbar />
                <div className="flex-1 flex items-center justify-center p-4">
                    <Card className="max-w-md w-full text-center p-8 border-primary/20 shadow-2xl">
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ type: "spring", duration: 0.8 }}
                        >
                            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                                <Check className="w-10 h-10 text-primary" />
                            </div>
                            <h2 className="text-3xl font-bold mb-4">{t('earlyAccess.success.title')}</h2>
                            <p className="text-muted-foreground mb-8">
                                {t('earlyAccess.success.description')}
                            </p>
                            <Button onClick={() => window.location.href = "/"} className="w-full">
                                {t('earlyAccess.success.home')}
                            </Button>
                        </motion.div>
                    </Card>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background flex flex-col">
            <Navbar />
            <div className="flex-1 flex flex-col items-center justify-center p-4 relative overflow-hidden">
                {/* Background blobs */}
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl -z-10" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl -z-10" />

                <div className="w-full max-w-lg">
                    <div className="mb-8 text-center">
                        <h1 className="text-4xl font-bold mb-2 tracking-tight">{t('earlyAccess.title')}</h1>
                        <p className="text-muted-foreground">{t('earlyAccess.subtitle')}</p>

                        {/* Progress Bar */}
                        <div className="h-1 w-full bg-secondary mt-8 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-primary"
                                initial={{ width: "0%" }}
                                animate={{ width: `${(step / 4) * 100}%` }} // Updated to 4 steps
                                transition={{ duration: 0.5 }}
                            />
                        </div>
                    </div>

                    <AnimatePresence mode="wait">
                        {step === 1 && (
                            <motion.div
                                key="step1"
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                            >
                                <Card className="border-border/50 shadow-lg backdrop-blur-sm bg-card/95">
                                    <CardHeader>
                                        <CardTitle className="text-center">{t('earlyAccess.steps.1.title')}</CardTitle>
                                        <CardDescription className="text-center">{t('earlyAccess.steps.1.description')}</CardDescription>
                                    </CardHeader>
                                    <CardContent className="grid gap-3">
                                        {AUDIENCE_OPTIONS.map((option) => (
                                            <Button
                                                key={option.id}
                                                variant="outline"
                                                className={`h-auto p-4 justify-between items-center text-left text-lg hover:border-primary hover:bg-primary/5 transition-all group relative ${answers.question_1.includes(option.id) ? "border-primary bg-primary/5" : ""
                                                    }`}
                                                onClick={() => handleOptionSelect("question_1", option.id)}
                                            >
                                                <div className="flex items-center gap-4">
                                                    {/* Custom Round Checkbox */}
                                                    <div className={`w-5 h-5 min-w-[1.25rem] rounded-full border-2 flex items-center justify-center transition-colors ${answers.question_1.includes(option.id)
                                                        ? "border-primary bg-primary"
                                                        : "border-muted-foreground/30 group-hover:border-primary/50"
                                                        }`}>
                                                        {answers.question_1.includes(option.id) && (
                                                            <div className="w-2 h-2 rounded-full bg-background" />
                                                        )}
                                                    </div>

                                                    <span className="font-medium text-foreground/80 group-hover:text-foreground transition-colors whitespace-normal leading-tight">
                                                        {option.label}
                                                    </span>
                                                </div>

                                                {/* Styled Icon on the right */}
                                                <div className="pl-2 shrink-0">
                                                    <option.icon className="w-6 h-6 text-primary opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all" strokeWidth={2} />
                                                </div>
                                            </Button>
                                        ))}
                                    </CardContent>
                                    <CardFooter>
                                        <Button
                                            onClick={handleNextStep}
                                            className="w-full text-lg py-6 group shadow-lg"
                                            disabled={answers.question_1.length === 0}
                                        >
                                            {t('earlyAccess.steps.1.next')}
                                            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                        </Button>
                                    </CardFooter>
                                </Card>
                            </motion.div>
                        )}


                        {step === 2 && (
                            <motion.div
                                key="step2"
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                            >
                                <Card className="border-border/50 shadow-lg backdrop-blur-sm bg-card/95">
                                    <CardHeader>
                                        <div className="flex items-center mb-2">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="w-fit -ml-2 text-muted-foreground"
                                                onClick={() => {
                                                    if (answers.estimationType) {
                                                        setAnswers(prev => ({ ...prev, estimationType: null }));
                                                    } else {
                                                        setStep(1);
                                                    }
                                                }}
                                            >
                                                {t('earlyAccess.steps.2.back')}
                                            </Button>
                                        </div>
                                        <CardTitle>{answers.estimationType ? t('earlyAccess.steps.2.title') : t('earlyAccess.steps.2.titleEstimated')}</CardTitle>
                                        {!answers.estimationType && (
                                            <CardDescription>{t('earlyAccess.steps.2.description')}</CardDescription>
                                        )}
                                    </CardHeader>
                                    <CardContent className="grid gap-4">
                                        {!answers.estimationType && (
                                            <>
                                                <Button
                                                    variant="outline"
                                                    className="h-auto p-6 justify-between items-center text-lg hover:border-primary hover:bg-primary/5 transition-all group"
                                                    onClick={() => handleEstimationTypeSelect("weight")}
                                                >
                                                    <div className="flex flex-col text-left">
                                                        <span className="font-semibold text-xl">{t('earlyAccess.steps.2.options.weight.label')}</span>
                                                        <span className="text-sm text-muted-foreground font-normal mt-1">{t('earlyAccess.steps.2.options.weight.sub')}</span>
                                                    </div>
                                                    <Scale className="w-8 h-8 text-primary opacity-80 group-hover:scale-110 transition-transform" />
                                                </Button>

                                                <Button
                                                    variant="outline"
                                                    className="h-auto p-6 justify-between items-center text-lg hover:border-primary hover:bg-primary/5 transition-all group"
                                                    onClick={() => handleEstimationTypeSelect("sets")}
                                                >
                                                    <span className="font-semibold text-xl">{t('earlyAccess.steps.2.options.sets')}</span>
                                                    <Package className="w-8 h-8 text-primary opacity-80 group-hover:scale-110 transition-transform" />
                                                </Button>
                                            </>
                                        )}

                                        {answers.estimationType === "weight" && (
                                            <div className="py-8 px-4 flex flex-col items-center gap-8">
                                                <div className="text-5xl font-bold text-primary tabular-nums">
                                                    {answers.weightValue >= 50 ? "+50" : answers.weightValue} <span className="text-2xl text-muted-foreground">kg</span>
                                                </div>

                                                <Slider
                                                    value={[answers.weightValue]}
                                                    min={0}
                                                    max={50}
                                                    step={2}
                                                    onValueChange={handleWeightChange}
                                                    className="w-full max-w-[80%]"
                                                />

                                                <p className="text-center text-muted-foreground text-sm">
                                                    {t('earlyAccess.steps.2.weight.label')}
                                                </p>

                                                <Button
                                                    className="w-full text-lg py-6 mt-4"
                                                    onClick={confirmWeightSelection}
                                                >
                                                    {t('earlyAccess.steps.2.weight.confirm')}
                                                </Button>
                                            </div>
                                        )}

                                        {answers.estimationType === "sets" && (
                                            OWNERSHIP_OPTIONS.map((option) => (
                                                <Button
                                                    key={option.id}
                                                    variant="outline"
                                                    className="h-auto p-4 justify-between text-lg hover:border-primary hover:bg-primary/5 transition-all"
                                                    onClick={() => handleOptionSelect("question_2", option.id)}
                                                >
                                                    {option.label}
                                                    <div className="w-4 h-4 rounded-full border border-primary/30" />
                                                </Button>
                                            ))
                                        )}
                                    </CardContent>
                                </Card>
                            </motion.div>
                        )}

                        {step === 3 && (
                            <motion.div
                                key="step3"
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                            >
                                <Card className="border-border/50 shadow-lg backdrop-blur-sm bg-card/95">
                                    <CardHeader>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="w-fit -ml-2 mb-2 text-muted-foreground"
                                            onClick={() => setStep(2)}
                                        >
                                            {t('earlyAccess.steps.3.back')}
                                        </Button>
                                        <CardTitle className="text-center mb-2">{t('earlyAccess.steps.3.title')}</CardTitle>
                                        <CardDescription className="text-center">{t('earlyAccess.steps.3.description')}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex flex-wrap gap-3 justify-center">
                                            {POPULAR_THEMES.map((theme) => (
                                                <Button
                                                    key={theme}
                                                    variant={answers.question_3.includes(theme) ? "default" : "outline"}
                                                    className={`h-auto py-2 px-4 rounded-full text-base transition-all ${answers.question_3.includes(theme)
                                                        ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md transform scale-105"
                                                        : "hover:border-primary/50 text-muted-foreground"
                                                        }`}
                                                    onClick={() => handleOptionSelect("question_3", theme)}
                                                >
                                                    {theme}
                                                </Button>
                                            ))}

                                            <Button
                                                variant={answers.otherSeries ? "default" : "outline"}
                                                className={`h-auto py-2 px-4 rounded-full text-base border-dashed ${answers.otherSeries ? "bg-primary text-primary-foreground" : "text-muted-foreground"
                                                    }`}
                                                onClick={() => setInputOtherOpen(true)}
                                            >
                                                {answers.otherSeries ? t('earlyAccess.steps.3.otherAdded') : t('earlyAccess.steps.3.other')}
                                                <Plus className="ml-2 w-4 h-4" />
                                            </Button>
                                        </div>
                                    </CardContent>
                                    <CardFooter>
                                        <Button
                                            onClick={() => setStep(4)}
                                            className="w-full text-lg py-6 group mt-4"
                                        >
                                            {t('earlyAccess.steps.3.next')}
                                            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                        </Button>
                                    </CardFooter>
                                </Card>

                                {/* Dialog for "Other" series */}
                                <Dialog open={inputOtherOpen} onOpenChange={setInputOtherOpen}>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>{t('earlyAccess.steps.3.dialog.title')}</DialogTitle>
                                            <DialogDescription>
                                                {t('earlyAccess.steps.3.dialog.description')}
                                            </DialogDescription>
                                        </DialogHeader>
                                        <Textarea
                                            placeholder={t('earlyAccess.steps.3.dialog.placeholder')}
                                            value={answers.otherSeries}
                                            onChange={(e) => setAnswers(prev => ({ ...prev, otherSeries: e.target.value }))}
                                            className="min-h-[100px]"
                                        />
                                        <DialogFooter>
                                            <Button onClick={() => setInputOtherOpen(false)}>{t('earlyAccess.steps.3.dialog.save')}</Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </motion.div>
                        )}

                        {step === 4 && (
                            <motion.div
                                key="step4"
                                variants={containerVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                            >
                                <Card className="border-border/50 shadow-lg backdrop-blur-sm bg-card/95">
                                    <CardHeader>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="w-fit -ml-2 mb-2 text-muted-foreground"
                                            onClick={() => setStep(3)}
                                        >
                                            {t('earlyAccess.steps.4.back')}
                                        </Button>
                                        <CardTitle className="leading-tight">{t('earlyAccess.steps.4.title')}</CardTitle>
                                        <CardDescription className="text-base mt-2">
                                            {t('earlyAccess.steps.4.description')}
                                        </CardDescription>
                                    </CardHeader>
                                    <form onSubmit={handleSubmit}>
                                        <CardContent className="space-y-4 pt-4">
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium text-muted-foreground ml-1">
                                                    {t('earlyAccess.steps.4.emailLabel')}
                                                </label>
                                                <Input
                                                    type="email"
                                                    placeholder={t('earlyAccess.steps.4.placeholder')}
                                                    required
                                                    value={answers.email}
                                                    onChange={(e) => setAnswers(prev => ({ ...prev, email: e.target.value }))}
                                                    className="text-lg p-6"
                                                />
                                            </div>
                                        </CardContent>
                                        <CardFooter className="flex flex-col gap-3">
                                            <Button
                                                type="submit"
                                                className="w-full text-lg py-6"
                                                disabled={isSubmitting}
                                            >
                                                {isSubmitting ? t('earlyAccess.steps.4.submitting') : t('earlyAccess.steps.4.submit')}
                                            </Button>
                                            <p className="text-xs text-muted-foreground text-center">
                                                {t('earlyAccess.steps.4.security')}
                                            </p>
                                        </CardFooter>
                                    </form>
                                </Card>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
