import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "react-i18next";

const CookiesPolicy = () => {
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
          {t('cookies.title')}
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('cookies.sections.1.title')}</h2>
            <p>{t('cookies.sections.1.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('cookies.sections.2.title')}</h2>
            <p>{t('cookies.sections.2.content')}</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>{t('cookies.sections.2.list.0')}</li>
              <li>{t('cookies.sections.2.list.1')}</li>
              <li>{t('cookies.sections.2.list.2')}</li>
              <li>{t('cookies.sections.2.list.3')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('cookies.sections.3.title')}</h2>
            <p>{t('cookies.sections.3.content')}</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">{t('cookies.sections.4.title')}</h2>
            <p>{t('cookies.sections.4.content')}</p>
          </section>

        </div>
      </div>
    </div>
  );
};

export default CookiesPolicy;
