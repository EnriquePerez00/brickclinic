import { Blocks, Mail, MapPin, Phone } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 text-xl font-extrabold mb-4">
              <Blocks className="h-6 w-6" />
              Brickclinic
            </div>
            <p className="text-sm opacity-70 leading-relaxed max-w-xs">
              {t('footer.brand.description')}
            </p>
            <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/20 text-accent text-xs font-semibold">
              {t('footer.brand.badge')}
            </div>
          </div>

          {/* Navigation */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">{t('footer.navigation.title')}</h4>
            <ul className="space-y-2 text-sm opacity-70">
              <li><a href="#servicios" className="hover:opacity-100 transition-opacity">{t('footer.navigation.links.services')}</a></li>
              <li><a href="#como-funciona" className="hover:opacity-100 transition-opacity">{t('footer.navigation.links.howItWorks')}</a></li>
              <li><a href="#faq" className="hover:opacity-100 transition-opacity">{t('footer.navigation.links.faq')}</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">{t('footer.legal.title')}</h4>
            <ul className="space-y-2 text-sm opacity-70">
              <li><Link to="/privacy" className="hover:opacity-100 transition-opacity">{t('footer.legal.links.privacy')}</Link></li>
              <li><Link to="/terms" className="hover:opacity-100 transition-opacity">{t('footer.legal.links.terms')}</Link></li>
              <li><Link to="/about" className="hover:opacity-100 transition-opacity">{t('footer.legal.links.about')}</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold mb-4 text-sm uppercase tracking-wider opacity-70">{t('footer.contact.title')}</h4>
            <ul className="space-y-3 text-sm opacity-70">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" /> info@brickclinic.es
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" /> {t('footer.contact.location')}
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-background/10 pt-8 pb-4">
          <p className="text-xs text-muted-foreground/60 text-center max-w-4xl mx-auto mb-4 leading-relaxed">
            {t('footer.disclaimer')}
          </p>
          <div className="text-center text-xs opacity-50">
            {t('footer.copyright')}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
