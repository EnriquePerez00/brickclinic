import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const MESSAGES = [
  {
    headline: "¡Rescata tus recuerdos del fondo del cajón!",
    body: "¿Tienes una montaña de piezas mezcladas que solían ser naves y castillos? En Brick Clinic utilizamos tecnología de IA para identificar, clasificar y reconstruir tus sets favoritos a partir de ese caos de ladrillos. No dejes que tus recuerdos cojan polvo.",
    cta: "¡Quiero recuperar mis sets ahora!"
  },
  {
    headline: "De \"montaña de piezas\" a \"sets listos para jugar\"",
    body: "Olvídate de pasar horas buscando esa pieza que falta. Envíanos tu cubo de LEGO mezclado y nosotros nos encargamos del resto: limpieza, clasificación por IA y reconstrucción completa. Tú solo preocúpate de disfrutar el re-estreno.",
    cta: "Calcula tu envío y prueba el servicio"
  },
  {
    headline: "Restauración profesional de LEGO con IA",
    body: "Recuperamos el valor de tu colección. Gracias a nuestro sistema avanzado de reconocimiento, convertimos kilos de piezas sueltas en sets icónicos listos para montar o vender. Servicio integral de limpieza y completado de sets.",
    cta: "Empieza tu restauración aquí"
  }
];

export function EarlyAccessPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState(MESSAGES[0]);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if popup has already been shown in this session
    const hasShown = sessionStorage.getItem("earlyAccessPopupShown");
    if (hasShown) return;

    // Select random message
    const randomIndex = Math.floor(Math.random() * MESSAGES.length);
    setMessage(MESSAGES[randomIndex]);

    const timer = setTimeout(() => {
      setIsOpen(true);
      sessionStorage.setItem("earlyAccessPopupShown", "true");
    }, 20000); // 20 seconds delay

    return () => clearTimeout(timer);
  }, []);

  const handleCTA = () => {
    setIsOpen(false);
    navigate("/early-access");
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[900px] p-0 gap-0 overflow-hidden">
        <div className="grid md:grid-cols-[2fr_1fr] h-[500px]">
          <div className="relative h-full">
            <img
              src="/lego_technic_contrast.png"
              alt="Before and After LEGO Technic sets"
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent md:hidden" />
          </div>
          <div className="p-8 flex flex-col justify-center gap-6 bg-background h-full overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-xl md:text-2xl font-bold text-primary leading-tight">
                {message.headline}
              </DialogTitle>
              <DialogDescription className="text-base text-muted-foreground mt-4 leading-relaxed">
                {message.body}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-2 sm:justify-start">
              <Button
                onClick={handleCTA}
                className="w-full text-lg font-semibold py-6 shadow-lg hover:shadow-xl transition-all whitespace-normal h-auto"
              >
                {message.cta}
              </Button>
            </DialogFooter>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
