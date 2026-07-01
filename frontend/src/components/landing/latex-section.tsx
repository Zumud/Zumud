import { ArrowRight, Braces, Download, ExternalLink, FileCode2 } from "lucide-react";
import { Button } from "@/components/ui/button";

const OUTPUTS = [
  {
    icon: Download,
    title: "Download PDF",
    description: "Ready to send.",
  },
  {
    icon: FileCode2,
    title: "Keep the source",
    description: "Own the full .tex file.",
  },
  {
    icon: ExternalLink,
    title: "Edit in Overleaf",
    description: "Change every detail.",
  },
];

export default function LatexSection() {
  return (
    <section id="latex" className="section scroll-mt-20">
      <div className="container-page">
        <div className="grid items-center gap-10 lg:grid-cols-[1fr_0.9fr] lg:gap-16">
          <div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Built with LaTeX
            </h2>
            <p className="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">
              Precise PDF. Full source. No locked template.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              {OUTPUTS.map((output) => {
                const Icon = output.icon;
                return (
                  <div key={output.title} className="flex items-start gap-4">
                    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-brand">
                      <Icon className="size-5" />
                    </span>
                    <div>
                      <h3 className="font-semibold">{output.title}</h3>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {output.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            <Button asChild variant="outline" size="lg" className="mt-8 w-fit">
              <a href="#hero-form">
                Build with LaTeX
                <ArrowRight className="size-4" />
              </a>
            </Button>
          </div>

          <div className="surface overflow-hidden shadow-xl shadow-brand/5">
            <div className="flex items-center justify-between border-b border-border/70 px-5 py-4">
              <div className="flex items-center gap-2">
                <Braces className="size-5 text-brand" />
                <span className="font-mono text-sm font-semibold">resume.tex</span>
              </div>
              <span className="rounded-full bg-success/10 px-2.5 py-1 text-xs font-medium text-success">
                Compiled
              </span>
            </div>
            <div className="overflow-hidden bg-muted/35 p-5 font-mono text-xs leading-6 text-muted-foreground sm:p-7 sm:text-sm">
              <p><span className="text-[var(--accent2)]">\documentclass</span>{"{resume}"}</p>
              <p><span className="text-[var(--accent2)]">\begin</span>{"{document}"}</p>
              <p className="pl-4 text-foreground">\name{"{Your Name}"}</p>
              <p className="pl-4"><span className="text-brand">\section</span>{"{Experience}"}</p>
              <p className="pl-8">\role{"{Product Designer}"}</p>
              <p className="pl-8">\impact{"{Improved activation by 28\\%}"}</p>
              <p className="pl-4"><span className="text-brand">\section</span>{"{Skills}"}</p>
              <p className="pl-8">\keywords{"{Research, Figma, SaaS}"}</p>
              <p><span className="text-[var(--accent2)]">\end</span>{"{document}"}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
