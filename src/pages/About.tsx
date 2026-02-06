import { Link } from "react-router-dom";
import { ArrowLeft, Blocks, Heart, Recycle, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

const About = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-3xl">
        <Link to="/">
          <Button variant="ghost" size="sm" className="mb-8 gap-2">
            <ArrowLeft className="h-4 w-4" /> Volver al inicio
          </Button>
        </Link>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground mb-8">
          Sobre Nosotros
        </h1>

        <div className="prose prose-sm max-w-none text-muted-foreground space-y-6">
          <p className="text-lg leading-relaxed">
            Brickclinic nace de una pasión compartida: devolver la vida a miles de piezas de construcción que acumulan polvo en cajas olvidadas.
          </p>

          <p>
            Somos un equipo de entusiastas dedicados a clasificar, limpiar y organizar colecciones de bricks. No somos una fábrica automatizada: somos artesanos que tratan cada pieza con el cuidado que merece.
          </p>

          <div className="grid sm:grid-cols-2 gap-6 my-10">
            {[
              { icon: Blocks, title: "Artesanía", desc: "Cada pieza se inspecciona y manipula a mano. Sin prisas, sin atajos." },
              { icon: Recycle, title: "Sostenibilidad", desc: "Reutilizar es mejor que comprar nuevo. Damos nueva vida a piezas existentes." },
              { icon: Heart, title: "Pasión", desc: "Somos coleccionistas que entienden el valor emocional de cada set." },
              { icon: Shield, title: "Confianza", desc: "Tus piezas nunca se mezclan con las de otros clientes. Transparencia total." },
            ].map((v) => (
              <div key={v.title} className="bg-secondary rounded-xl p-6 border border-border">
                <v.icon className="h-6 w-6 text-primary mb-3" />
                <h3 className="text-foreground font-bold mb-1">{v.title}</h3>
                <p className="text-sm text-muted-foreground">{v.desc}</p>
              </div>
            ))}
          </div>

          <p>
            Brickclinic es un servicio independiente. No estamos afiliados, respaldados ni conectados de ninguna forma con el Grupo LEGO. Todas las marcas registradas mencionadas pertenecen a sus respectivos propietarios.
          </p>

          <p>
            ¿Tienes preguntas? Escríbenos a <a href="mailto:hola@brickclinic.es" className="text-primary hover:underline">hola@brickclinic.es</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;
