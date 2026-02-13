import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en/translation.json';
import es from './locales/es/translation.json';
import ca from './locales/ca/translation.json';

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources: {
            en: { translation: en },
            es: { translation: es },
            ca: { translation: ca },
        },
        fallbackLng: 'en',
        supportedLngs: ['en', 'es', 'ca'],
        interpolation: {
            escapeValue: false, // not needed for react as it escapes by default
        },
        detection: {
            order: ['path', 'navigator'],
            lookupFromPathIndex: 0,
        },
    });

export default i18n;
