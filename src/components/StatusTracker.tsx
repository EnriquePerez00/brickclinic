import { motion } from "framer-motion";
import { Package, Droplets, Grid3X3, CheckCircle } from "lucide-react";

const statuses = [
  { icon: Package, label: "Recibido", done: true },
  { icon: Droplets, label: "Lavado", done: true },
  { icon: Grid3X3, label: "Clasificando", done: false, active: true },
  { icon: CheckCircle, label: "Listo", done: false },
];

const StatusTracker = () => {
  return (
    <section className="py-24 bg-secondary">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            Seguimiento en Tiempo Real
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Consulta el estado de tu pedido en cualquier momento. Transparencia total.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto bg-card rounded-xl p-8 border border-border shadow-sm"
        >
          <div className="flex items-center justify-between relative">
            {/* Progress bar */}
            <div className="absolute top-6 left-0 right-0 h-1 bg-border rounded-full" />
            <div className="absolute top-6 left-0 h-1 bg-primary rounded-full" style={{ width: "45%" }} />

            {statuses.map((s) => (
              <div key={s.label} className="relative flex flex-col items-center gap-2 z-10">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors ${
                    s.done
                      ? "bg-primary border-primary"
                      : s.active
                      ? "bg-primary/20 border-primary animate-pulse"
                      : "bg-card border-border"
                  }`}
                >
                  <s.icon
                    className={`h-5 w-5 ${
                      s.done ? "text-primary-foreground" : s.active ? "text-primary" : "text-muted-foreground"
                    }`}
                  />
                </div>
                <span className={`text-xs font-medium ${s.done || s.active ? "text-foreground" : "text-muted-foreground"}`}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default StatusTracker;
