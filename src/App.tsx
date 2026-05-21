import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { HelmetProvider } from "react-helmet-async";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LanguageRedirector from "./components/LanguageRedirector";
import Index from "./pages/Index";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import CookiesPolicy from "./pages/CookiesPolicy";
import LegalNotice from "./pages/LegalNotice";
import About from "./pages/About";
import NotFound from "./pages/NotFound";
import EarlyAccessPage from "./pages/EarlyAccessPage";
import Login from "./pages/admin/Login";
import Dashboard from "./pages/admin/Dashboard";
import InventoryGenerator from "./pages/admin/InventoryGenerator";
import SimilarSets from "./pages/admin/SimilarSets";
import MOCGenerator from "./pages/admin/MOCGenerator";
import BlogList from "./pages/blog/BlogList";
import BlogPost from "./pages/blog/BlogPost";
import BlogLayout from "./components/BlogLayout";
import WhatsAppChatWidget from "./components/WhatsAppChatWidget";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <WhatsAppChatWidget />
          <Routes>
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="/admin/login" element={<Login />} />
            <Route path="/admin/dashboard" element={<Dashboard />} />
            <Route path="/admin/inventory-generator" element={<Dashboard />} />
            <Route path="/admin/similar-sets" element={<Dashboard />} />
            <Route path="/admin/moc-generator" element={<Dashboard />} />

            {/* Language Redirector for Root */}
            <Route path="/" element={<LanguageRedirector />} />

            {/* Localized Public Routes */}
            <Route path="/:lang">
              <Route index element={<Index />} />
              <Route path="privacy" element={<Privacy />} />
              <Route path="terms" element={<Terms />} />
              <Route path="cookies" element={<CookiesPolicy />} />
              <Route path="legal" element={<LegalNotice />} />
              <Route path="about" element={<About />} />
              <Route path="early-access" element={<EarlyAccessPage />} />
              <Route path="blog" element={<BlogLayout />}>
                <Route index element={<BlogList />} />
                <Route path=":slug" element={<BlogPost />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Route>

            {/* Catch-all for non-localized paths that aren't admin (redirect to root to be handled) */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
