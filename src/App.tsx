import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";
import About from "./pages/About";
import NotFound from "./pages/NotFound";
import EarlyAccessPage from "./pages/EarlyAccessPage";
import Login from "./pages/admin/Login";
import Dashboard from "./pages/admin/Dashboard";
import InventoryGenerator from "./pages/admin/InventoryGenerator";
import SimilarSets from "./pages/admin/SimilarSets";
import MOCGenerator from "./pages/admin/MOCGenerator";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/about" element={<About />} />
          <Route path="/early-access" element={<EarlyAccessPage />} />


          {/* Admin Routes */}
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="/admin/login" element={<Login />} />
          <Route path="/admin/dashboard" element={<Dashboard />} />
          {/* Legacy redirects */}
          <Route path="/admin/inventory-generator" element={<Dashboard />} />
          <Route path="/admin/similar-sets" element={<Dashboard />} />
          <Route path="/admin/moc-generator" element={<Dashboard />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
