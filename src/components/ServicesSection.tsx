import { motion } from "framer-motion";
import { Droplets, Puzzle, Lightbulb, PackageOpen } from "lucide-react";
import imgClasificacion from "@/assets/Brickclinic1.png";
import imgMontaje from "@/assets/Brickclinic3.png";
import imgPropuestas from "@/assets/Brickclinic4.png";
import imgDevolucion from "@/assets/Brickclinic6.png";

const services = [
  {
    icon: Droplets,
    title: "Clasificación e Higienización",
    description:
      "Separamos todas tus piezas por tipo, color y tamaño. Cada brick pasa por un proceso de limpieza manual con productos seguros para el plástico ABS. Tus piezas quedan impecables y perfectamente organizadas.",
    color: "text-primary",
    bg: "bg-primary/10",
    image: imgClasificacion,
  },
  {
    icon: Puzzle,
    title: "Montaje de Sets",
    description:
      "Completamos tus sets a partir de las piezas originales que ya tienes. Identificamos las que faltan y las conseguimos para que puedas volver a construir como el primer día.",
    color: "text-accent",
    bg: "bg-accent/10",
    image: imgMontaje,
  },
  {
    icon: Lightbulb,
    title: "Propuestas de Sets Alternativos",
    description:
      "Ideamos y sugerimos construcciones alternativas u originales a partir de tus piezas existentes, complementándolas con piezas nuevas si es necesario. Creatividad sin límites.",
    color: "text-brick-yellow",
    bg: "bg-brick-yellow/10",
    image: imgPropuestas,
  },
  {
    icon: PackageOpen,
    title: "Devolución de Sets Separados",
    description:
      "Te devolvemos cada set perfectamente separado, embolsado e inventariado. Listo para guardar, exponer o regalar. Todo en orden.",
    color: "text-brick-red",
    bg: "bg-brick-red/10",
    image: imgDevolucion,
  },
];

const ServicesSection = () => {
  return (
    <section id="servicios" className="py-24 bg-secondary/50">
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

        <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {services.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group bg-card rounded-2xl overflow-hidden shadow-sm border border-border hover:shadow-xl transition-all duration-300"
            >
              <div className="relative h-64 overflow-hidden">
                <img
                  src={s.image}
                  alt={s.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-80" />
                <div className="absolute bottom-4 left-4 right-4 flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-background/90 backdrop-blur-sm ${s.color}`}>
                    <s.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-bold text-white shadow-sm">{s.title}</h3>
                </div>
              </div>

              <div className="p-6">
                <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                  {s.description}
                </p>
                <div className="pt-4 border-t border-border flex items-center justify-between">
                  <span className="text-xs text-muted-foreground italic">
                    Consultar disponibilidad
                  </span>
                  <a href="#presupuesto" className="text-sm font-semibold text-primary hover:underline">
                    Solicitar
                  </a>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
