import { Blocks, Mail, MapPin, Phone } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-12 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 text-xl font-extrabold mb-4">
              <Blocks className="h-6 w-6" />
              Brickclinic
            </div>
            <p className="text-sm opacity-70 leading-relaxed max-w-xs">
              Artesanos del brick. Clasificamos, montamos y proponemos sets a partir de tus piezas LEGO con cuidado y pasión.
            </p>
            <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/20 text-accent text-xs font-semibold">
              ♻️ Comprometidos con la economía circular
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">Navegación</h4>
            <ul className="space-y-2 text-sm opacity-70">
              <li><a href="#servicios" className="hover:opacity-100 transition-opacity">Servicios</a></li>
              <li><a href="#como-funciona" className="hover:opacity-100 transition-opacity">Cómo Funciona</a></li>
              <li><a href="#faq" className="hover:opacity-100 transition-opacity">Preguntas Frecuentes</a></li>
            </ul>

            <h4 className="font-bold mt-6 mb-4 text-sm uppercase tracking-wider opacity-70">Legal</h4>
            <ul className="space-y-2 text-sm opacity-70">
              <li><Link to="/privacy" className="hover:opacity-100 transition-opacity">Política de Privacidad</Link></li>
              <li><Link to="/terms" className="hover:opacity-100 transition-opacity">Términos del Servicio</Link></li>
              <li><Link to="/about" className="hover:opacity-100 transition-opacity">Sobre Nosotros</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">Contacto</h4>
            <ul className="space-y-3 text-sm opacity-70">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" /> info@brickclinic.es
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" /> Barcelona, España
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-background/10 pt-8 text-center text-xs opacity-50">
          © 2026 Brickclinic. Todos los derechos reservados.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
