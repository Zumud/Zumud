const LOGOS = [
  { src: "/logos/google.svg", alt: "Google", className: "h-7" },
  { src: "/logos/microsoft.svg", alt: "Microsoft", className: "h-7" },
  { src: "/logos/amazon.svg", alt: "Amazon", className: "h-7" },
  { src: "/logos/meta.svg", alt: "Meta", className: "h-6" },
  { src: "/logos/apple.svg", alt: "Apple", className: "h-9" },
];

export default function CompanyLogosSection() {
  return (
    <section className="border-y border-border/60 bg-muted/30 py-12">
      <div className="container-page">
        <p className="text-center text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Tailored for roles at companies like these
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-x-10 gap-y-6 md:gap-x-14">
          {LOGOS.map((logo) => (
            <img
              key={logo.alt}
              src={logo.src}
              alt={`${logo.alt} logo`}
              className={`${logo.className} w-auto opacity-60 grayscale transition duration-300 hover:opacity-100 hover:grayscale-0 dark:opacity-70 dark:brightness-0 dark:invert dark:hover:opacity-100`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
