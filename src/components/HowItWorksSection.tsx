import { motion } from "framer-motion";
import { Package, Droplets, Grid3X3, CheckCircle } from "lucide-react";

const steps = [
  {
    icon: Package,
    title: "Envía tus bricks",
    description: "Recogemos tus piezas sueltas o sets incompletos. Te enviamos una caja con portes incluidos.",
  },
  {
    icon: Droplets,
    title: "Pesamos, lavamos y secamos",
    description: "Cada pieza pasa por un proceso de limpieza manual con agua templada y jabón neutro.",
  },
  {
    icon: Grid3X3,
    title: "Clasificamos e identificamos",
    description: "Separamos por color, tipo y set. Identificamos sets completos o piezas de alto valor.",
  },
  {
    icon: CheckCircle,
    title: "Recibe tu colección",
    description: "Sets organizados, inventario detallado y opción de completar lo que falte. ¡Como nuevos!",
  },
];

const HowItWorksSection = () => {
  return (
    <section id="como-funciona" className="py-24">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            Cómo Funciona
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Un proceso transparente de principio a fin. Tú solo envías, nosotros hacemos el resto.
          </p>
        </motion.div>

        <div className="max-w-3xl mx-auto relative">
          {/* Vertical line */}
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-border md:-translate-x-px" />

          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className={`relative flex items-start gap-6 mb-12 md:mb-16 ${
                i % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse"
              }`}
            >
              {/* Icon node */}
              <div className="relative z-10 flex-shrink-0 w-12 h-12 rounded-full bg-primary flex items-center justify-center shadow-lg md:mx-auto">
                <step.icon className="h-5 w-5 text-primary-foreground" />
              </div>

              {/* Content */}
              <div className={`bg-card rounded-xl p-6 border border-border shadow-sm flex-1 ${
                i % 2 === 0 ? "md:text-right md:mr-8" : "md:text-left md:ml-8"
              }`}>
                <span className="text-xs font-bold text-primary uppercase tracking-wider">
                  Paso {i + 1}
                </span>
                <h3 className="text-lg font-bold text-foreground mt-1 mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
