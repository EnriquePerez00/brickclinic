import { motion } from "framer-motion";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "¿Aceptáis todo tipo de piezas?",
    answer:
      "Aceptamos y trabajamos únicamente con piezas y minifiguras originales de LEGO®. Si nos haces llegar otro tipo de juguetes o piezas de otras marcas, las separaremos y te las devolveremos junto con tu pedido.",
  },
  {
    question: "¿Podéis limpiar cualquier tipo de suciedad?",
    answer:
      "Limpiamos e higienizamos industrialmente utilizando tecnología hospitalaria, pero no hacemos milagros. Nos reservamos el derecho de devolverte piezas dañadas, no higienizables (rotuladores, corrosión, manchas de ácidos) o piezas con plástico abrasado por el sol o rozamiento.",
  },
  {
    question: "¿Garantizáis que no habrá errores en la clasificación?",
    answer:
      "Trabajamos con piezas originales de segunda mano, proveedores oficiales y LEGO.com. Podemos cometer errores en la clasificación o falta de piezas... somos humanos. Si es el caso, avísanos y repondremos los posibles errores.",
  },
  {
    question: "¿Conseguís las minifiguras originales de los sets?",
    answer:
      "Te podemos sugerir minifiguras de la misma serie que el set, pero no necesariamente las específicas que acompañan el set original si son muy caras u objetos de coleccionista difíciles de conseguir. Siempre te propondremos un sustituto original y posible.",
  },
  {
    question: "¿Tengo que enviar los sets desmontados?",
    answer:
      "Aceptamos sets desordenados, piezas mezcladas y sets semimontados. Te aconsejamos que los desmontes ya que ocuparán menos espacio y el envío será más eficiente. Pero si nos las envías juntas, también nos gusta desmontar LEGO® y lo haremos por ti. Si algunas piezas no pudiesen separarse (¿pegamento?, ¿torsiones?, ¿plástico semidesgastado?), las dejaremos en un lado y las devolveremos.",
  },
  {
    question: "¿Qué puedo esperar obtener de mis cajas de LEGO®?",
    answer:
      "Hay múltiples factores que afectan al número, variedad y coste de los sets que podemos recuperar. Un set completo al 80% es más barato de reconstruir que uno al 50%. Además, si es de series 'top ventas' como Star Wars™, LEGO® City o LEGO® Technic, hay más volumen y mejor precio de recambios que en series minoritarias.",
  },
  {
    question: "¿Recuperáis sets antiguos?",
    answer:
      "Recuperamos sets posteriores a 1960. Sin embargo, ten en cuenta que el importe de las piezas para estos sets antiguos puede costar algo más debido a su escasez.",
  },
  {
    question: "¿Qué tipo de diseños me proponéis con mis piezas?",
    answer:
      "Depende de la variedad y temática de tus piezas. Con varios sets de la misma temática semicompletos podemos sugerirte sets y nuevas creaciones de la misma serie y tendremos más opciones que con un cajón de ladrillos 2x2 y 3x3 de colores azules, blancos y rojos. Cuantas menos series de sets mezcles mejor, y cuanta más variedad de piezas mejor.",
  },
  {
    question: "¿Es vuestro proceso seguro para niños con alergias?",
    answer:
      "Sí. Al no utilizar suavizantes ni perfumes industriales, y basar nuestra limpieza en procesos físicos (ultrasonidos) y enzimáticos, minimizamos cualquier riesgo de dermatitis por contacto.",
  },
  {
    question: "¿El proceso daña las piezas de LEGO®?",
    answer:
      "Al contrario. El lavado ultrasónico es mucho más delicado que un lavavajillas doméstico. Al no haber fricción mecánica agresiva, el brillo original del plástico se mantiene por más tiempo y las conexiones siguen siendo perfectas.",
  },
];

const FAQSection = () => {
  // Schema.org structured data for FAQ Rich Snippets
  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <section id="faq" className="py-24">
      {/* Schema.org Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            Preguntas Frecuentes
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            Resolvemos tus dudas más comunes. Si no encuentras la respuesta, escríbenos.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, i) => (
              <AccordionItem key={i} value={`faq-${i}`}>
                <AccordionTrigger className="text-left text-foreground font-semibold">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
};

export default FAQSection;
