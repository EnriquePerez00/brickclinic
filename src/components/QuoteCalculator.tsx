import { motion } from "framer-motion";
import { Truck, Search, Hammer, Archive } from "lucide-react";

const steps = [
  {
    icon: Truck,
    title: "1) Envío inicial",
    price: "Variable",
    description: (
      <>
        <p className="mb-2">
          Podemos ayudarte a solicitar el envío, pero te pedimos que nos lo envíes por tu cuenta.
          Estimación ida y vuelta nacional:
        </p>
        <ul className="list-disc pl-5 space-y-1 text-sm">
          <li><strong>5 kg:</strong> Entre 10€ y 18€</li>
          <li><strong>15 kg:</strong> Entre 20€ y 28€</li>
          <li><strong>30 kg:</strong> Entre 35€ y 50€</li>
        </ul>
        <p className="mt-2 text-xs italic">
          Disponemos de descuentos con proveedores logísticos, podemos gestionarlo por ti si prefieres.
        </p>
      </>
    ),
  },
  {
    icon: Search,
    title: "2) Higienización y Análisis",
    price: "9,95€ / kg",
    description: (
      <>
        <p>Higienización, identificación de piezas defectuosas y análisis de reconstrucción o transformación.</p>
        <p className="mt-2 text-primary font-bold">Ejemplo: 5 kg = 49,75€</p>
      </>
    ),
  },
  {
    icon: Hammer,
    title: "3) Reconstrucción (a demanda)",
    price: "14,90€ gestión + piezas",
    description: (
      <>
        <p className="mb-2">Reconstrucción o transformación en nuevos sets.</p>
        <p className="text-sm">Coste de piezas (aprox):</p>
        <ul className="list-disc pl-5 space-y-1 text-sm">
          <li><strong>Pequeñas (1x1, studs):</strong> 0,01€ - 0,03€ / ud</li>
          <li><strong>Medianas (2x4, 2x2):</strong> 0,05€ - 0,12€ / ud</li>
        </ul>
        <p className="mt-2 text-xs">Piezas grandes o minifiguras pueden tener precios más elevados. Siempre informamos antes.</p>
      </>
    ),
  },
  {
    icon: Archive,
    title: "4) Clasificación y Devolución",
    price: "9,90€ / 500 piezas útiles",
    description: (
      <>
        <p>Gestión de devolución de todo el contenido o únicamente el contenido útil.</p>
        <p className="mt-2 text-primary font-bold">Ejemplo: 5 kg (aprox. 4000 piezas) = 79,20€</p>
        <p className="text-xs text-muted-foreground mt-1">Redondeamos al múltiplo más cercano por arriba.</p>
      </>
    ),
  },
];

const QuoteCalculator = () => {
  return (
    <section id="cuanto-cuesta" className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            Cuánto Cuesta
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Te explicamos nuestros costes con total transparencia. Sin sorpresas.
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="bg-card rounded-xl p-6 shadow-sm border border-border relative overflow-hidden group hover:shadow-md transition-shadow"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <step.icon className="w-24 h-24" />
              </div>

              <div className="relative z-10">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 text-primary">
                  <step.icon className="w-6 h-6" />
                </div>

                <h3 className="font-bold text-lg mb-2 text-foreground">{step.title}</h3>
                <div className="text-2xl font-extrabold text-primary mb-4">{step.price}</div>

                <div className="text-sm text-muted-foreground leading-relaxed">
                  {step.description}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default QuoteCalculator;
