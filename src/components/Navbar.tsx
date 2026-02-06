import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Blocks, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const navLinks = [
  { label: "Servicios", href: "#servicios" },
  { label: "Cómo Funciona", href: "#como-funciona" },
  { label: "Cuánto Cuesta", href: "#cuanto-cuesta" },
  { label: "FAQ", href: "#faq" },
];

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="container mx-auto flex items-center justify-between h-20 px-4 relative">
        <a href="/" className="flex items-center gap-2 text-primary font-extrabold text-2xl relative z-10">
          <Blocks className="h-8 w-8" />
          <span>Brickclinic</span>
        </a>

        {/* Desktop Navigation - Centered */}
        <div className="hidden md:flex items-center gap-8 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-base font-bold text-foreground/80 hover:text-primary transition-colors uppercase tracking-wide"
            >
              {l.label}
            </a>
          ))}
        </div>

        <div className="hidden md:block relative z-10 w-[140px]">
          {/* Spacer to balance if needed, or actions area */}
        </div>

        <button className="md:hidden text-foreground relative z-10" onClick={() => setOpen(!open)}>
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden overflow-hidden bg-background border-b border-border"
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
              <a href="#presupuesto" onClick={() => setOpen(false)} className="w-full">
                <Button size="sm" className="w-full">Solicitar Presupuesto</Button>
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
