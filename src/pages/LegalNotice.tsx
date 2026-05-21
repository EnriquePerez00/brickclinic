import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";

const LegalNotice = () => {
  const { t, i18n } = useTranslation();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to={`/${i18n.language}`}>
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> {t('about.back')}
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          {t('legal.title')}
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('legal.general.title')}</h2>
            <p>{t('legal.general.text')}</p>
            <ul className="list-none pl-0 space-y-1 mt-4">
              <li className="font-medium text-foreground">{t('legal.general.name')}</li>
              <li>{t('legal.general.nif')}</li>
              <li>{t('legal.general.address')}</li>
              <li>{t('legal.general.email')}</li>
              <li>{t('legal.general.phone')}</li>
              <li>{t('legal.general.registry')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('legal.property.title')}</h2>
            <p>{t('legal.property.text')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('legal.trademarks.title')}</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('legal.trademarks.lego')}</li>
              <li>{t('legal.trademarks.original')}</li>
              <li>{t('legal.trademarks.nominative')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('legal.nature.title')}</h2>
            <p>{t('legal.nature.text')}</p>
          </section>

        </div>
      </div>
    </div>
  );
};

export default LegalNotice;
