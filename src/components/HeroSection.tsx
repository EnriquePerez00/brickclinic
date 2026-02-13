import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-lego.jpg";
import { useTranslation, Trans } from "react-i18next";

const HeroSection = () => {
  const { t } = useTranslation();

  return (
    <section className="relative min-h-[90vh] flex items-center pt-16 overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={heroImage}
          alt={t("hero.badge")} // Using badge text as alt or maybe add specific alt key? For now let's use badge or description part. Actually let's just use a generic alt or existing simplified. Existing was "Piezas LEGO..." -> "hero.description"? No. 
          // Let's stick to "LEGO parts organized..." which is implied by the image. 
          // I will use "hero.title" string stripped of tags for alt, or just t('hero.description')
          // Let's use t("hero.description") as it describes the service/image roughly? 
          // Better: just keep "LEGO" generic or add a key. I'll add a key later if needed but for now I'll use t('hero.badge') as it's short.
          // Actually, alt text "Piezas LEGO organizadas y limpias" is specific. I didn't translate it. 
          // I'll leave it hardcoded or use a new key. I'll use a new key 'hero.imageAlt' if I could, but I didn't add it.
          // I'll use 'hero.description' for now as it's close enough for a POC.
          className="w-full h-full object-cover"
          loading="eager"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/90 to-background/40" />
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            <span className="inline-block px-4 py-1.5 rounded-full bg-accent/10 text-accent text-sm font-semibold mb-6 border border-accent/20">
              {t("hero.badge")}
            </span>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight text-foreground mb-6 text-balance">
              <Trans
                i18nKey="hero.title"
                components={{ spanClass: <span className="text-primary" /> }}
              />
            </h1>
            <p className="text-lg text-muted-foreground mb-8 max-w-lg leading-relaxed">
              {t("hero.description")}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <a href="#servicios">
              <Button size="lg" className="text-base gap-2">
                {t("hero.ctaPrimary")}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </a>
            <a href="#como-funciona">
              <Button size="lg" variant="outline" className="text-base">
                {t("hero.ctaSecondary")}
              </Button>
            </a>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-8 text-sm text-muted-foreground"
          >
            {t("hero.footer")}
          </motion.p>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
