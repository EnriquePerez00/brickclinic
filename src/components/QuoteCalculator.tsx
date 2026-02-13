import { motion } from "framer-motion";
import { Truck, Search, Hammer, Archive } from "lucide-react";

import { useTranslation } from "react-i18next";


const QuoteCalculator = () => {
  const { t } = useTranslation();

  const steps = [
    {
      icon: Truck,
      title: t('pricing.steps.shipping.title'),
      price: t('pricing.steps.shipping.price'),
      description: (
        <>
          <p className="mb-2">
            {t('pricing.steps.shipping.description.p1')}
          </p>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            <li><strong>5 kg:</strong> {t('pricing.steps.shipping.description.list.small')}</li>
            <li><strong>15 kg:</strong> {t('pricing.steps.shipping.description.list.medium')}</li>
            <li><strong>30 kg:</strong> {t('pricing.steps.shipping.description.list.large')}</li>
          </ul>
          <div className="mt-3 bg-green-100 text-green-800 text-xs font-bold px-2 py-1 rounded-md border border-green-200 inline-block">
            {t('pricing.steps.shipping.description.promo')}
          </div>
          <p className="mt-2 text-xs italic">
            {t('pricing.steps.shipping.description.note')}
          </p>
        </>
      ),
    },
    {
      icon: Search,
      title: t('pricing.steps.analysis.title'),
      price: t('pricing.steps.analysis.price'),
      description: (
        <>
          <p>{t('pricing.steps.analysis.description.main')}</p>
          <p className="mt-2 text-primary font-bold">{t('pricing.steps.analysis.description.example')}</p>
        </>
      ),
    },
    {
      icon: Hammer,
      title: t('pricing.steps.reconstruction.title'),
      price: t('pricing.steps.reconstruction.price'),
      description: (
        <>
          <p className="mb-2">{t('pricing.steps.reconstruction.description.main')}</p>
          <p className="text-sm">{t('pricing.steps.reconstruction.description.costTitle')}</p>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            <li><strong>{t('pricing.steps.reconstruction.description.list.small').split(':')[0]}:</strong>{t('pricing.steps.reconstruction.description.list.small').split(':')[1]}</li>
            <li><strong>{t('pricing.steps.reconstruction.description.list.medium').split(':')[0]}:</strong>{t('pricing.steps.reconstruction.description.list.medium').split(':')[1]}</li>
          </ul>
          <p className="mt-2 text-xs">{t('pricing.steps.reconstruction.description.note')}</p>
        </>
      ),
    },
    {
      icon: Archive,
      title: t('pricing.steps.return.title'),
      price: t('pricing.steps.return.price'),
      description: (
        <>
          <p>{t('pricing.steps.return.description.main')}</p>
          <p className="mt-2 text-primary font-bold">{t('pricing.steps.return.description.example')}</p>
          <p className="text-xs text-muted-foreground mt-1">{t('pricing.steps.return.description.note')}</p>
        </>
      ),
    },
  ];

  return (
    <section id="cuanto-cuesta" className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            {t('pricing.title')}
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            {t('pricing.subtitle')}
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="bg-card rounded-xl p-6 shadow-sm border border-border group hover:shadow-md transition-shadow flex flex-col items-center text-center"
            >
              <div className="p-4 rounded-full bg-primary/5 mb-6 group-hover:bg-primary/10 transition-colors">
                <step.icon className="w-12 h-12 text-primary" />
              </div>

              <div className="w-full">
                <h3 className="font-bold text-lg mb-2 text-foreground">{step.title}</h3>
                <div className="text-2xl font-extrabold text-primary mb-4">{step.price}</div>

                <div className="text-sm text-muted-foreground leading-relaxed text-left">
                  {step.description}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default QuoteCalculator;
