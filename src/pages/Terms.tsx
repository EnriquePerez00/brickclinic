import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const Terms = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> Volver al inicio
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          Términos y Condiciones de Servicio
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-sm text-muted-foreground">Última actualización: Febrero 2026</p>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">1. Sobre el Servicio</h2>
            <p>Brickclinic ofrece servicios de clasificación, limpieza, montaje de sets, propuestas de construcción creativa y devoluciones organizadas para piezas de construcción tipo ladrillo. Nuestros servicios se realizan manualmente con cuidado profesional, pero implican la manipulación de piezas de plástico pequeñas y delicadas.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">2. Descargo de Responsabilidad de Propiedad Intelectual</h2>
            <p className="font-semibold text-foreground">AVISO IMPORTANTE: Brickclinic es una iniciativa independiente.</p>
            <p><strong>No estamos afiliados, respaldados, patrocinados ni conectados de ninguna manera con LEGO Group</strong> ni con ninguna de sus subsidiarias o filiales.</p>
            <p>LEGO®, el logotipo de LEGO®, la Minifigura, DUPLO®, y todas las demás marcas comerciales y la imagen comercial de LEGO® son propiedad de LEGO Group. Todas las referencias a productos LEGO® en este sitio web se realizan únicamente con fines identificativos y descriptivos para indicar la compatibilidad de nuestros servicios.</p>
            <p>Brickclinic no fabrica, vende ni distribuye productos LEGO® nuevos. Proporcionamos servicios de posventa independientes exclusivamente para piezas que ya son propiedad de nuestros clientes.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">3. Limitación de Responsabilidad — Riesgos de Manipulación</h2>
            <p>Al utilizar nuestros servicios, el cliente reconoce y acepta lo siguiente:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Desgaste y antigüedad:</strong> Los ladrillos de construcción, especialmente las piezas antiguas o muy usadas, pueden mostrar signos de desgaste, decoloración o microarañazos. Estos son inherentes a la edad y el uso previo de las piezas y no son causados por nuestro proceso de manipulación.</li>
              <li><strong>Riesgo de rotura:</strong> Brickclinic no asume responsabilidad por la rotura de piezas que, debido a su antigüedad, estado previo, fragilidad o estrés del material (como el síndrome de plástico quebradizo), puedan dañarse durante la manipulación profesional habitual. Aunque ejercemos el máximo cuidado, existe un riesgo inherente al manipular piezas envejecidas.</li>
              <li><strong>Degradación de pegatinas e impresiones:</strong> Las piezas impresas y con pegatinas pueden sufrir degradación durante el proceso de limpieza debido a su antigüedad o al estado del adhesivo. Las tratamos con especial cuidado (limpieza a mano), pero no podemos garantizar su preservación total si ya están deterioradas.</li>
              <li><strong>Piezas faltantes:</strong> No somos responsables de las piezas que ya faltaban en la colección del cliente antes de la recepción. Nuestro inventario se basa estrictamente en lo que recibimos físicamente.</li>
              <li><strong>Límite de responsabilidad:</strong> En cualquier caso, la responsabilidad total de Brickclinic por cualquier reclamación derivada de nuestros servicios no excederá el precio del servicio pagado por el cliente para el pedido específico en cuestión.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">4. Envíos y Tránsito</h2>
            <p>Brickclinic no se hace responsable de la pérdida o daño que ocurra durante el tránsito hacia nuestras instalaciones. Recomendamos encarecidamente utilizar servicios de envío asegurados y con seguimiento. Una vez que las piezas se entregan en nuestras instalaciones, están bajo nuestro cuidado y cubiertas por las limitaciones descritas en la Sección 3.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">5. Obligaciones del Cliente</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>El cliente debe enviar únicamente ladrillos de construcción originales y compatibles.</li>
              <li>No se deben incluir piezas no originales, baterías, componentes electrónicos dañados, objetos extraños, ni suciedad excesiva/peligrosa.</li>
              <li>El cliente es responsable de describir con precisión el contenido de su envío.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">6. Precios y Pagos</h2>
            <p>Los precios se determinan en función del peso, volumen y los servicios específicos solicitados. Se proporcionará un presupuesto final tras la recepción e inspección, el cual debe ser aprobado por el cliente antes de comenzar el trabajo. Si el cliente rechaza el presupuesto final, las piezas serán devueltas a cargo del cliente.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">7. Pedidos No Reclamados</h2>
            <p>Si un pedido no es recogido, pagado o si el cliente no responde a las notificaciones durante más de 90 días después del aviso de finalización, Brickclinic se reserva el derecho de disponer de las piezas a su discreción para cubrir los costes de almacenamiento y gestión.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">8. Ley Aplicable</h2>
            <p>Estos términos se rigen por las leyes de España. Cualquier disputa relacionada con estos términos o nuestros servicios se someterá a la jurisdicción exclusiva de los tribunales de Barcelona, España.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">9. Contacto</h2>
            <p>Para cualquier pregunta sobre estos términos, por favor contáctenos en <a href="mailto:info@brickclinic.es" className="text-primary hover:underline">info@brickclinic.es</a>.</p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Terms;
