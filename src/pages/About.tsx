import { Link } from "react-router-dom";
import { ArrowLeft, Blocks, Heart, Recycle, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";

const About = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> {t('about.back')}
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          {t('about.title')}
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-lg leading-relaxed">
            {t('about.intro')}
          </p>

          <p>
            {t('about.description')}
          </p>

          <div className="grid sm:grid-cols-2 gap-6 my-10">
            {[
              { icon: Blocks, title: t('about.values.craftsmanship.title'), desc: t('about.values.craftsmanship.desc') },
              { icon: Recycle, title: t('about.values.sustainability.title'), desc: t('about.values.sustainability.desc') },
              { icon: Heart, title: t('about.values.passion.title'), desc: t('about.values.passion.desc') },
              { icon: Shield, title: t('about.values.trust.title'), desc: t('about.values.trust.desc') },
            ].map((v) => (
              <div key={v.title} className="bg-secondary rounded-xl p-6 border border-border">
                <v.icon className="h-6 w-6 text-primary mb-3" />
                <h3 className="text-foreground font-bold mb-1">{v.title}</h3>
                <p className="text-sm text-muted-foreground">{v.desc}</p>
              </div>
            ))}
          </div>

          <p>
            {t('about.disclaimer')}
          </p>

          <p>
            {t('about.contact')} <a href="mailto:hola@brickclinic.es" className="text-primary hover:underline">hola@brickclinic.es</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;
