import { motion } from "framer-motion";
import { Package, Droplets, Grid3X3, Truck, Hammer, PackageOpen } from "lucide-react";
import { useTranslation } from "react-i18next";

const StatusTracker = () => {
  const { t } = useTranslation();

  const statuses = [
    { icon: Truck, label: t('statusTracker.statuses.shipping'), done: true },
    { icon: PackageOpen, label: t('statusTracker.statuses.received'), done: true },
    { icon: Droplets, label: t('statusTracker.statuses.hygiene'), done: true },
    { icon: Grid3X3, label: `${t('statusTracker.statuses.categorization')} (*)`, done: false, active: true },
    { icon: Hammer, label: t('statusTracker.statuses.reconstruction'), done: false },
    { icon: Truck, label: t('statusTracker.statuses.returnShipping'), done: false },
  ];

  return (
    <section className="py-24 bg-secondary">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-4">
            {t('statusTracker.title')}
          </h2>
          <p className="text-muted-foreground max-w-md mx-auto">
            {t('statusTracker.description')}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto bg-card rounded-xl p-8 border border-border shadow-sm mb-8"
        >
          {/* Mobile Scroll Wrapper */}
          <div className="overflow-x-auto pb-4 -mx-4 px-4 sm:overflow-visible sm:pb-0 sm:px-0">
            <div className="flex items-start justify-between relative min-w-[600px] sm:min-w-0">
              {/* Progress bar line */}
              <div className="absolute top-6 left-0 right-0 h-1 bg-border rounded-full hidden sm:block" />
              <div className="absolute top-6 left-0 h-1 bg-primary rounded-full hidden sm:block" style={{ width: "60%" }} />

              {statuses.map((s, index) => {
                const hasMarker = s.label.includes("(*)");
                const cleanLabel = s.label.replace(" (*)", "");

                return (
                  <div key={index} className="relative flex flex-col items-center gap-3 z-10 flex-1 px-1">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors shrink-0 bg-card ${s.done
                        ? "bg-primary border-primary"
                        : s.active
                          ? "bg-primary/10 border-primary animate-pulse"
                          : "border-border"
                        }`}
                    >
                      <s.icon
                        className={`h-5 w-5 ${s.done ? "text-primary-foreground" : s.active ? "text-primary" : "text-muted-foreground"
                          }`}
                      />
                    </div>

                    <div className="text-center">
                      <span className={`text-xs font-bold block ${s.active || s.done ? "text-foreground" : "text-muted-foreground"}`}>
                        {cleanLabel}
                        {hasMarker && <span className="text-primary ml-0.5">*</span>}
                      </span>

                      {/* Marker Text */}
                      {hasMarker && (
                        <motion.div
                          initial={{ opacity: 0, y: 5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mt-2 text-[10px] leading-tight font-medium text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20 max-w-[120px] mx-auto"
                        >
                          {t('statusTracker.marker')}
                        </motion.div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Quotes and Estimation */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="text-center max-w-2xl mx-auto space-y-6"
        >
          <p className="text-lg italic font-medium text-foreground/80 border-l-4 border-primary/50 pl-4 inline-block">
            {t('statusTracker.quote.text')}
            <span className="block text-sm font-normal text-muted-foreground mt-1 not-italic">{t('statusTracker.quote.author')}</span>
          </p>

          <p className="text-xs text-muted-foreground leading-relaxed max-w-lg mx-auto bg-muted/50 p-4 rounded-lg">
            {t('statusTracker.estimation')}
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default StatusTracker;
