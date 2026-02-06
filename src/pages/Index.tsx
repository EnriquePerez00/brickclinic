import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import ServicesSection from "@/components/ServicesSection";
import HowItWorksSection from "@/components/HowItWorksSection";
import ThemesMarquee from "@/components/ThemesMarquee";
import BeforeAfterSection from "@/components/BeforeAfterSection";
import QuoteCalculator from "@/components/QuoteCalculator";
import StatusTracker from "@/components/StatusTracker";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <HeroSection />
        <ServicesSection />
        <ThemesMarquee />
        <HowItWorksSection />
        <BeforeAfterSection />
        <QuoteCalculator />
        <StatusTracker />
      </main>
      <Footer />
    </div>
  );
};

export default Index;
