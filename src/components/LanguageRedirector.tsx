import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const LanguageRedirector = () => {
    const { i18n } = useTranslation();
    const navigate = useNavigate();

    useEffect(() => {
        // Check if we are at the root path
        if (window.location.pathname === '/') {
            const browserLang = navigator.language;
            let targetLang = 'en';

            if (browserLang.startsWith('es')) {
                targetLang = 'es';
            } else if (browserLang.startsWith('ca')) {
                targetLang = 'ca';
            }

            // If i18next has already detected a language and it's one of ours, use it
            if (['es', 'ca', 'en'].includes(i18n.language)) {
                targetLang = i18n.language;
            }

            // Ensure we redirect to the supported language
            if (!['es', 'ca', 'en'].includes(targetLang)) {
                targetLang = 'en';
            }

            navigate(`/${targetLang}`, { replace: true });
        }
    }, [navigate, i18n.language]);

    return null;
};

export default LanguageRedirector;
