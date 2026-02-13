import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Blocks, Menu, X, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();

  const currentLang = i18n.language;

  const navLinks = [
    { label: t("navbar.items.services"), href: "#servicios" },
    { label: t("navbar.items.howItWorks"), href: "#como-funciona" },
    { label: t("navbar.items.pricing"), href: "#cuanto-cuesta" },

    { label: t("navbar.items.faq"), href: "#faq" },
  ];

  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    const currentPath = location.pathname;
    // Replace the language segment in the URL (assuming /:lang/...)
    // If we are at root (handled by redirector), this might be tricky, but usually we are at /:lang
    let newPath = currentPath;
    const pathSegments = currentPath.split('/');

    if (['es', 'ca', 'en'].includes(pathSegments[1])) {
      pathSegments[1] = lang;
      newPath = pathSegments.join('/');
    } else {
      // Fallback if structure is different (e.g. at root before redirect? shouldn't happen)
      newPath = `/${lang}${currentPath}`;
    }

    // Preserve hash if any (location.hash might not be available in newPath string construction directly if not careful, but navigate works on path)
    navigate(newPath + location.hash);
  };

  const navigateToEarlyAccess = () => {
    navigate(`/${currentLang}/early-access`);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-md border-b border-border/50 shadow-sm">
      <div className="container mx-auto flex items-center justify-between h-24 px-6 relative">
        <a href={`/${currentLang}`} className="flex items-center gap-3 text-primary font-extrabold text-2xl relative z-10 hover:opacity-80 transition-opacity">
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

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="text-foreground/70 hover:text-primary">
                <Globe className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleLanguageChange('es')}>
                Español
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleLanguageChange('ca')}>
                Català
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleLanguageChange('en')}>
                English
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            onClick={navigateToEarlyAccess}
            className="animate-pulse shadow-lg hover:shadow-xl transition-all"
          >
            {t("navbar.earlyAccess")}
          </Button>
        </div>

        <div className="hidden lg:block relative z-10 w-[20px]">
          {/* Spacer for balance */}
        </div>

        <div className="flex items-center gap-4 lg:hidden relative z-10">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="text-foreground/70 hover:text-primary">
                <Globe className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleLanguageChange('es')}>ES</DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleLanguageChange('ca')}>CA</DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleLanguageChange('en')}>EN</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <button className="text-foreground" onClick={() => setOpen(!open)}>
            {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
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
                  navigateToEarlyAccess();
                }}
                size="sm"
                className="w-full"
              >
                {t("navbar.requestAccess")}
              </Button>
              <Button
                onClick={() => {
                  setOpen(false);
                  navigateToEarlyAccess();
                }}
                variant="secondary"
                className="w-full"
              >
                {t("navbar.earlyAccess")}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
