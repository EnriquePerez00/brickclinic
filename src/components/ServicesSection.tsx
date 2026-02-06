import { motion } from "framer-motion";
import { Droplets, Grid3X3, Puzzle } from "lucide-react";

const services = [
  {
    icon: Droplets,
    title: "Sanitización",
    description:
      "Limpieza profunda pieza a pieza. Eliminamos suciedad, polvo y manchas con productos seguros para el plástico ABS. Tus bricks quedan como nuevos.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    icon: Grid3X3,
    title: "Clasificación",
    description:
      "Ordenamos tus piezas por color, tipo o set original. Utilizamos catálogos oficiales para identificar cada pieza con precisión milimétrica.",
    color: "text-accent",
    bg: "bg-accent/10",
  },
  {
    icon: Puzzle,
    title: "Completado de Sets",
    description:
      "Identificamos las piezas que faltan para restaurar tus sets. Buscamos las piezas exactas para que puedas volver a construir como el primer día.",
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
          <p className="text-muted-foreground max-w-md mx-auto">
            No somos una fábrica rápida, somos artesanos. Nos tomamos el tiempo para dejar tus piezas perfectas.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {services.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="bg-card rounded-xl p-8 shadow-sm border border-border hover:shadow-md transition-shadow"
            >
              <div className={`inline-flex p-3 rounded-xl ${s.bg} mb-6`}>
                <s.icon className={`h-6 w-6 ${s.color}`} />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">{s.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {s.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
