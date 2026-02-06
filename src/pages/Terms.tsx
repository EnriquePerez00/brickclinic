import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const Terms = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> Volver al inicio
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          Terms of Service
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-sm text-muted-foreground">Last updated: February 2026</p>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">1. About the Service</h2>
            <p>Brickclinic provides sorting, cleaning, set assembly, creative building proposals, and organized return services for construction toy bricks. Our services are performed manually with professional care, but involve handling small, delicate plastic parts.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">2. Intellectual Property Disclaimer</h2>
            <p>Brickclinic is an independent service provider. We are <strong>not affiliated with, endorsed by, approved by, or in any way connected to the LEGO Group</strong> or any of its subsidiaries or affiliates.</p>
            <p>LEGO®, the LEGO® logo, the Minifigure, DUPLO®, and all other LEGO® trademarks and trade dress are the property of the LEGO Group. All references to LEGO® products on this website are made solely for identification and descriptive purposes.</p>
            <p>Brickclinic does not manufacture, sell, or distribute LEGO® products. We provide independent aftermarket services exclusively for pieces already owned by our customers.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">3. Limitation of Liability — Handling Risk</h2>
            <p>By using our services, the customer acknowledges and accepts the following:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Wear and tear:</strong> Construction toy bricks, especially older or heavily used pieces, may show signs of wear, discoloration, or micro-scratches. These are inherent to the age and prior use of the pieces and are not caused by our handling process.</li>
              <li><strong>Breakage risk:</strong> While we exercise maximum care in handling all pieces, there is an inherent risk of breakage, especially with brittle, aged, or damaged parts. Brickclinic shall not be held liable for breakage of parts that were already weakened, cracked, or structurally compromised prior to receipt.</li>
              <li><strong>Sticker and print degradation:</strong> Printed and stickered parts may suffer degradation during the cleaning process due to their age or adhesive condition. We handle these with extra care but cannot guarantee their preservation.</li>
              <li><strong>Missing pieces:</strong> We are not responsible for pieces that were already missing from the customer's collection upon receipt. Our inventory is based on what we physically receive.</li>
              <li><strong>Maximum liability:</strong> In any case, Brickclinic's total liability for any claim arising from our services shall not exceed the service fee paid by the customer for the specific order in question.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">4. Shipping and Transit</h2>
            <p>Brickclinic is not responsible for loss or damage occurring during transit. We recommend using insured shipping services. Once pieces are delivered to our facility, they are under our care and covered by the limitations described in Section 3.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">5. Customer Obligations</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>The customer must only send genuine, original construction toy bricks.</li>
              <li>Non-original parts, batteries, electronic components, and non-brick items must not be included.</li>
              <li>The customer is responsible for accurately describing the contents of their shipment.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">6. Pricing and Payment</h2>
            <p>Prices are determined based on weight, volume, and the specific services requested. A final quote will be provided after inspection and must be approved by the customer before work begins. If the customer rejects the quote, pieces will be returned at the customer's expense.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">7. Uncollected Orders</h2>
            <p>If an order is not collected or the customer becomes unresponsive for more than 90 days after notification of completion, Brickclinic reserves the right to dispose of the pieces at its discretion.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">8. Governing Law</h2>
            <p>These terms are governed by the laws of Spain. Any disputes shall be submitted to the courts of Madrid, Spain.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-foreground mt-8 mb-3">9. Contact</h2>
            <p>For any questions about these terms, please contact us at hola@brickclinic.es.</p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Terms;
