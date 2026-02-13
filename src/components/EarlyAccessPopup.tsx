import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export function EarlyAccessPopup() {
  const { t } = useTranslation();
  const messages = t('earlyAccessPopup.messages', { returnObjects: true }) as Array<{ headline: string, body: string, cta: string }>;

  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState(messages[0]);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if popup has already been shown in this session
    const hasShown = sessionStorage.getItem("earlyAccessPopupShown");
    if (hasShown) return;

    // Select random message
    const randomIndex = Math.floor(Math.random() * messages.length);
    setMessage(messages[randomIndex]);

    const timer = setTimeout(() => {
      setIsOpen(true);
      sessionStorage.setItem("earlyAccessPopupShown", "true");
    }, 20000); // 20 seconds delay

    return () => clearTimeout(timer);
  }, [messages]);

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
              alt={t('earlyAccessPopup.imageAlt')}
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
