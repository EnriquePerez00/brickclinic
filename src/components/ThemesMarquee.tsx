const themes = [
  "Star Wars", "Technic", "City", "Architecture", "Creator Expert",
  "Ideas", "Speed Champions", "Harry Potter", "Ninjago", "Friends",
  "Marvel", "DC Comics", "Icons", "Botanical",
];

const ThemesMarquee = () => {
  return (
    <section className="py-12 bg-primary overflow-hidden">
      <div className="flex animate-marquee whitespace-nowrap">
        {[...themes, ...themes].map((theme, i) => (
          <span
            key={i}
            className="mx-8 text-lg font-bold text-primary-foreground/80 uppercase tracking-widest select-none"
          >
            {theme}
          </span>
        ))}
      </div>
    </section>
  );
};

export default ThemesMarquee;
