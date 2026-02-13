import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation, Trans } from "react-i18next";

const Privacy = () => {
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
          {t('privacy.title')}
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-sm text-muted-foreground">{t('privacy.lastUpdated')}</p>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.1.title')}</h2>
            <p>{t('privacy.sections.1.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.2.title')}</h2>
            <p>{t('privacy.sections.2.content')}</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>{t('privacy.sections.2.list.0')}</li>
              <li>{t('privacy.sections.2.list.1')}</li>
              <li>{t('privacy.sections.2.list.2')}</li>
              <li>{t('privacy.sections.2.list.3')}</li>
              <li>{t('privacy.sections.2.list.4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.3.title')}</h2>
            <p>{t('privacy.sections.3.content')}</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>{t('privacy.sections.3.list.0')}</li>
              <li>{t('privacy.sections.3.list.1')}</li>
              <li>{t('privacy.sections.3.list.2')}</li>
              <li>{t('privacy.sections.3.list.3')}</li>
              <li>{t('privacy.sections.3.list.4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.4.title')}</h2>
            <p>{t('privacy.sections.4.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.5.title')}</h2>
            <p>{t('privacy.sections.5.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.6.title')}</h2>
            <p>{t('privacy.sections.6.content')}</p>
            <ul className="list-disc pl-6 space-y-1">
              <li><Trans i18nKey="privacy.sections.6.list.0" /></li>
              <li><Trans i18nKey="privacy.sections.6.list.1" /></li>
              <li><Trans i18nKey="privacy.sections.6.list.2" /></li>
              <li><Trans i18nKey="privacy.sections.6.list.3" /></li>
              <li><Trans i18nKey="privacy.sections.6.list.4" /></li>
              <li><Trans i18nKey="privacy.sections.6.list.5" /></li>
            </ul>
            <p className="mt-2">{t('privacy.sections.6.footer')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.7.title')}</h2>
            <p>{t('privacy.sections.7.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.8.title')}</h2>
            <p>{t('privacy.sections.8.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('privacy.sections.9.title')}</h2>
            <p><Trans i18nKey="privacy.sections.9.content" /></p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Privacy;
