import { useState } from "react";
import { motion } from "framer-motion";
import beforeImg from "@/assets/carrusel1.png";
import afterImg from "@/assets/carrusel2.png";

const BeforeAfterSection = () => {
  const [position, setPosition] = useState(50);

  return (
    <section id="nosotros" className="py-24 bg-secondary">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            El Resultado Habla por Sí Solo
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Desliza para ver la transformación. De piezas olvidadas a colección restaurada.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          <div className="relative rounded-xl overflow-hidden aspect-square select-none shadow-lg border border-border">
            {/* After (background) */}
            <img
              src={afterImg}
              alt="LEGO® después de la limpieza"
              className="absolute inset-0 w-full h-full object-cover"
              loading="lazy"
            />

            {/* Before (clipped) */}
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${position}%` }}
            >
              <img
                src={beforeImg}
                alt="LEGO® antes de la limpieza"
                className="w-full h-full object-cover"
                style={{ width: `${(100 / position) * 100}%`, maxWidth: "none" }}
                loading="lazy"
              />
            </div>

            {/* Slider handle */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-primary-foreground cursor-ew-resize z-10"
              style={{ left: `${position}%` }}
            >
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-primary border-2 border-primary-foreground flex items-center justify-center shadow-lg">
                <span className="text-primary-foreground text-xs font-bold">⟷</span>
              </div>
            </div>

            {/* Slider input */}
            <input
              type="range"
              min={5}
              max={95}
              value={position}
              onChange={(e) => setPosition(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
              aria-label="Comparar antes y después"
            />

            {/* Labels */}
            <span className="absolute top-4 left-4 bg-foreground/70 text-background px-3 py-1 rounded-full text-xs font-bold z-10">
              Antes
            </span>
            <span className="absolute top-4 right-4 bg-accent text-accent-foreground px-3 py-1 rounded-full text-xs font-bold z-10">
              Después
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default BeforeAfterSection;
