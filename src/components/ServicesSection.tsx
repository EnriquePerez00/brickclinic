import { motion } from "framer-motion";
import { Droplets, Puzzle, Lightbulb, PackageOpen } from "lucide-react";

const services = [
  {
    icon: Droplets,
    title: "Clasificación e Higienización",
    description:
      "Separamos todas tus piezas por tipo, color y tamaño. Cada brick pasa por un proceso de limpieza manual con productos seguros para el plástico ABS. Tus piezas quedan impecables y perfectamente organizadas.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: Puzzle,
    title: "Montaje de Sets",
    description:
      "Completamos tus sets a partir de las piezas originales que ya tienes. Identificamos las que faltan y las conseguimos para que puedas volver a construir como el primer día.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: Lightbulb,
    title: "Propuestas de Sets Alternativos",
    description:
      "Ideamos y sugerimos construcciones alternativas u originales a partir de tus piezas existentes, complementándolas con piezas nuevas si es necesario. Creatividad sin límites.",
    color: "text-brick-yellow",
    bg: "bg-brick-yellow/10",
  },
  {
    icon: PackageOpen,
    title: "Devolución de Sets Separados",
    description:
      "Te devolvemos cada set perfectamente separado, embolsado e inventariado. Listo para guardar, exponer o regalar. Todo en orden.",
    color: "text-brick-red",
    bg: "bg-brick-red/10",
  },
];

const ServicesSection = () => {
  return (
    <section id="servicios" className="py-24 bg-secondary">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            Nuestros Servicios
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto">
            Cada servicio es independiente. Elige lo que necesitas y nosotros nos encargamos del resto. Precios y alcance a medida.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {services.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-card rounded-xl p-8 shadow-sm border border-border hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex p-3 rounded-xl ${s.bg} mb-6`}>
                <s.icon className={`h-6 w-6 ${s.color}`} />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">{s.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {s.description}
              </p>
              <div className="mt-4 pt-4 border-t border-border">
                <span className="text-xs text-muted-foreground italic">
                  Alcance y precio a determinar según volumen y complejidad
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
