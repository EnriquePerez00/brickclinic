import { motion } from "framer-motion";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "¿Qué tipo de piezas aceptáis?",
    answer:
      "Aceptamos piezas originales LEGO® y LEGO® Technic en buen estado. No aceptamos piezas rotas, muy deterioradas, piezas de otras marcas, pilas ni componentes electrónicos.",
  },
  {
    question: "¿Clasificáis Minifiguras?",
    answer:
      "No clasificamos Minifiguras ni Mini-dolls. Si encontramos alguna entre tus piezas, la separaremos con cuidado y te la devolveremos junto con el resto de tu pedido.",
  },
  {
    question: "¿Puedo enviar piezas parcialmente montadas?",
    answer:
      "Lo ideal es que desmontéis las piezas antes de enviarlas para optimizar el embalaje. Pero si no tienes tiempo, nosotros nos encargamos sin problema.",
  },
  {
    question: "¿Cómo puedo estimar el peso de mis piezas?",
    answer:
      "Puedes pesarlas con una báscula de cocina o baño. Como referencia, una caja de zapatos llena de LEGO® pesa entre 1,5 y 2 kg. También puedes enviarnos una foto de la caja junto a un objeto de referencia y te damos una estimación.",
  },
  {
    question: "¿Cada servicio es independiente?",
    answer:
      "Sí, cada uno de nuestros servicios (clasificación e higienización, montaje de sets, propuestas de sets alternativos y devolución separada) se contrata de forma independiente. Puedes elegir solo los que necesites.",
  },
  {
    question: "¿Qué pasa si faltan piezas para completar un set?",
    answer:
      "Si faltan piezas, buscamos las originales necesarias para completar el set. Te informaremos del coste adicional antes de proceder con la compra.",
  },
  {
    question: "¿Podéis restaurar sets antiguos?",
    answer:
      "¡Sí! Podemos trabajar con sets de cualquier época. Ten en cuenta que si faltan piezas, puede que utilicemos versiones actuales del mismo brick como sustitución.",
  },
  {
    question: "¿Recibiré mis propias piezas de vuelta?",
    answer:
      "Por supuesto. Cada pedido se gestiona de forma individual. Tus piezas nunca se mezclan con las de otros clientes. Recibirás tus propios bricks, limpios y organizados.",
  },
  {
    question: "¿Tenéis alguna relación con LEGO®?",
    answer:
      "No. Brickclinic es un servicio independiente y no está afiliado, respaldado ni conectado de ninguna forma con el Grupo LEGO. LEGO® y sus marcas asociadas son propiedad del Grupo LEGO.",
  },
];

const FAQSection = () => {
  return (
    <section id="faq" className="py-24">
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
