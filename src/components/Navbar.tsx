import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Blocks, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const navLinks = [
  { label: "Servicios", href: "#servicios" },
  { label: "Cómo Funciona", href: "#como-funciona" },
  { label: "Cuánto Cuesta", href: "#cuanto-cuesta" },
  { label: "Precio", href: "#ejemplo-valor" },
  { label: "FAQ", href: "#faq" },
];

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-md border-b border-border/50 shadow-sm">
      <div className="container mx-auto flex items-center justify-between h-24 px-6 relative">
        <a href="/" className="flex items-center gap-3 text-primary font-extrabold text-2xl relative z-10 hover:opacity-80 transition-opacity">
          <Blocks className="h-8 w-8" />
          <span className="tracking-tight">Brickclinic</span>
        </a>

        {/* Desktop Navigation - Right Aligned */}
        <div className="hidden lg:flex items-center gap-10 ml-auto">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-[15px] font-semibold text-foreground/70 hover:text-primary transition-all duration-200 tracking-wide relative group"
            >
              {l.label}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all duration-200 group-hover:w-full"></span>
            </a>
          ))}
          <Button
            onClick={() => navigate("/early-access")}
            className="animate-pulse shadow-lg hover:shadow-xl transition-all"
          >
            Acceso Anticipado
          </Button>
        </div>

        <div className="hidden lg:block relative z-10 w-[20px]">
          {/* Spacer for balance */}
        </div>

        <button className="lg:hidden text-foreground relative z-10" onClick={() => setOpen(!open)}>
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="lg:hidden overflow-hidden bg-background border-b border-border"
          >
            <div className="flex flex-col gap-4 px-4 py-6">
              {navLinks.map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  {l.label}
                </a>
              ))}
              <Button
                onClick={() => {
                  setOpen(false);
                  navigate("/early-access");
                }}
                size="sm"
                className="w-full"
              >
                Solicitar Acceso
              </Button>
              <Button
                onClick={() => {
                  setOpen(false);
                  navigate("/early-access");
                }}
                variant="secondary"
                className="w-full"
              >
                Acceso Anticipado
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
