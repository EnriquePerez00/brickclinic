import { Blocks, Mail, MapPin, Phone } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-12 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 text-xl font-extrabold mb-4">
              <Blocks className="h-6 w-6" />
              BrickLink<span className="font-normal opacity-60">.es</span>
            </div>
            <p className="text-sm opacity-70 leading-relaxed max-w-xs">
              Artesanos del brick. Recuperamos, limpiamos y organizamos tus colecciones LEGO con
              cuidado y pasión.
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
              <li><a href="#nosotros" className="hover:opacity-100 transition-opacity">Nosotros</a></li>
              <li><a href="#sostenibilidad" className="hover:opacity-100 transition-opacity">Sostenibilidad</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">Contacto</h4>
            <ul className="space-y-3 text-sm opacity-70">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" /> hola@bricklink.es
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4" /> +34 612 345 678
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" /> Madrid, España
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-background/10 pt-8 text-center text-xs opacity-50">
          © {new Date().getFullYear()} BrickLink.es — Todos los derechos reservados. Solo piezas originales.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
