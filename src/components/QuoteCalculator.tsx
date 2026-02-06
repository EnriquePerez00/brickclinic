import { useState } from "react";
import { motion } from "framer-motion";
import { Calculator } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const QuoteCalculator = () => {
  const [weight, setWeight] = useState("");
  const pricePerKg = 25;
  const numWeight = parseFloat(weight) || 0;
  const minPrice = Math.round(numWeight * pricePerKg * 0.8);
  const maxPrice = Math.round(numWeight * pricePerKg * 1.2);

  return (
    <section id="sostenibilidad" className="py-24">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          {/* Info */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <span className="inline-block px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-semibold mb-4 border border-accent/20">
              ♻️ Sostenibilidad
            </span>
            <h2 className="text-3xl font-extrabold text-foreground mb-4">
              Calcula tu Presupuesto
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Cada kilo de LEGO que recuperamos es plástico que no acaba en un vertedero.
              Introduce el peso estimado de tus bricks y te daremos un rango orientativo.
            </p>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent" /> Envío con recogida gratuita desde 5 kg
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent" /> Presupuesto final tras inspección
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent" /> Sin compromiso
              </li>
            </ul>
          </motion.div>

          {/* Calculator card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-card rounded-xl p-8 border border-border shadow-sm"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-primary/10">
                <Calculator className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-lg font-bold text-foreground">Estimador Rápido</h3>
            </div>

            <label className="text-sm font-medium text-foreground mb-2 block">
              Peso estimado (kg)
            </label>
            <Input
              type="number"
              min={0}
              step={0.5}
              placeholder="Ej: 5"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              className="mb-6"
            />

            {numWeight > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="bg-secondary rounded-lg p-4 mb-6 text-center"
              >
                <p className="text-sm text-muted-foreground mb-1">Rango estimado</p>
                <p className="text-3xl font-extrabold text-foreground">
                  {minPrice}€ – {maxPrice}€
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Para {numWeight} kg · Precio final tras inspección
                </p>
              </motion.div>
            )}

            <Button className="w-full" size="lg">
              Solicitar Presupuesto
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default QuoteCalculator;
