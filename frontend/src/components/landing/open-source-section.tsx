import { Eye, Server, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GithubIcon } from "@/components/icons/github-icon";

const GITHUB_URL = "https://github.com/Zumud/Zumud";

const GUARANTEES = [
  {
    icon: Eye,
    title: "Read every line",
    description: "No hidden logic. Auditable in full.",
  },
  {
    icon: Server,
    title: "Self-host it",
    description: "Run Zumud on your own machine.",
  },
  {
    icon: ShieldCheck,
    title: "Own your data",
    description: "Your resume stays yours.",
  },
];

export default function OpenSourceSection() {
  return (
    <section id="open-source" className="section scroll-mt-20 border-y border-border/60 bg-muted/30">
      <div className="container-page">
        <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="max-w-xl">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Trust shouldn&apos;t require faith
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              The engine behind{" "}
              <span className="font-semibold text-foreground">3× more interviews</span>{" "}
              is fully open — read every line, run it yourself, keep your data.
            </p>

            <Button asChild variant="brand" size="lg" className="mt-8 w-fit">
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                <GithubIcon className="size-4" />
                Star us on GitHub
              </a>
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {GUARANTEES.map((item) => {
              const Icon = item.icon;
              return (
                <article
                  key={item.title}
                  className="surface group p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md"
                >
                  <div className="mb-5 flex items-center justify-between">
                    <div className="flex size-10 items-center justify-center rounded-xl bg-brand/10 text-brand">
                      <Icon className="size-5" />
                    </div>
                  </div>
                  <h3 className="font-semibold">{item.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {item.description}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
