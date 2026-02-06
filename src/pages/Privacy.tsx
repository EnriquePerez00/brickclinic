import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const Privacy = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> Volver al inicio
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          Política de Privacidad
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-sm text-muted-foreground">Última actualización: febrero 2026</p>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">1. Responsable del Tratamiento</h2>
            <p>Brickclinic (en adelante, "nosotros") es el responsable del tratamiento de los datos personales recogidos a través de este sitio web. Puedes contactarnos en: hola@brickclinic.es.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">2. Datos que Recogemos</h2>
            <p>Podemos recoger los siguientes datos personales:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Nombre y apellidos</li>
              <li>Dirección de correo electrónico</li>
              <li>Número de teléfono</li>
              <li>Dirección postal (para envíos y devoluciones)</li>
              <li>Datos de navegación (cookies, IP, tipo de navegador)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">3. Finalidad del Tratamiento</h2>
            <p>Tus datos se utilizan para:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Gestionar y procesar pedidos de servicios</li>
              <li>Comunicarnos contigo sobre el estado de tu pedido</li>
              <li>Enviar presupuestos y facturas</li>
              <li>Mejorar nuestros servicios y experiencia de usuario</li>
              <li>Cumplir con obligaciones legales</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">4. Base Legal</h2>
            <p>El tratamiento se basa en: tu consentimiento explícito, la ejecución de un contrato de servicio, y el cumplimiento de obligaciones legales aplicables conforme al RGPD (Reglamento General de Protección de Datos, UE 2016/679).</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">5. Conservación de Datos</h2>
            <p>Los datos se conservarán durante el tiempo necesario para cumplir con la finalidad para la que fueron recogidos y, en todo caso, durante los plazos legales de conservación aplicables.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">6. Derechos del Usuario (RGPD)</h2>
            <p>Tienes derecho a:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Acceso:</strong> Solicitar una copia de tus datos personales.</li>
              <li><strong>Rectificación:</strong> Corregir datos inexactos.</li>
              <li><strong>Supresión:</strong> Solicitar la eliminación de tus datos ("derecho al olvido").</li>
              <li><strong>Limitación:</strong> Restringir el tratamiento en determinadas circunstancias.</li>
              <li><strong>Portabilidad:</strong> Recibir tus datos en formato estructurado.</li>
              <li><strong>Oposición:</strong> Oponerte al tratamiento de tus datos.</li>
            </ul>
            <p className="mt-2">Para ejercer cualquiera de estos derechos, contacta con nosotros en hola@brickclinic.es.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">7. Cookies</h2>
            <p>Este sitio web puede utilizar cookies propias y de terceros para mejorar la experiencia de navegación. Puedes configurar tu navegador para rechazar cookies, aunque esto podría afectar a la funcionalidad del sitio.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">8. Transferencias Internacionales</h2>
            <p>No realizamos transferencias de datos personales fuera del Espacio Económico Europeo salvo que se garanticen las salvaguardias adecuadas conforme al RGPD.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">9. Contacto y Reclamaciones</h2>
            <p>Si consideras que tus derechos no han sido respetados, puedes presentar una reclamación ante la Agencia Española de Protección de Datos (AEPD) en <a href="https://www.aepd.es" className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">www.aepd.es</a>.</p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
