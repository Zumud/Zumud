import { ArrowRight, Check, FileText, ScanSearch, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

const SUPPORT_LINES = [
  "Clean, readable sections.",
  "Job-matched keywords.",
  "Built for ATS parsing.",
];

export default function SolutionSection() {
  return (
    <section id="ats-friendly" className="section scroll-mt-20">
      <div className="container-page">
        <div className="overflow-hidden rounded-3xl border border-brand/15 bg-brand-gradient-soft">
          <div className="grid lg:grid-cols-[0.9fr_1.1fr]">
            <div className="flex flex-col justify-center p-7 sm:p-10 lg:p-14">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                ATS-friendly by design
              </h2>
              <p className="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">
                Clean structure. Right keywords. Easy for ATS tools to read.
              </p>

              <ul className="mt-7 grid gap-3">
                {SUPPORT_LINES.map((line) => (
                  <li key={line} className="flex items-center gap-3 font-medium">
                    <span className="flex size-6 items-center justify-center rounded-full bg-brand text-white">
                      <Check className="size-3.5" />
                    </span>
                    {line}
                  </li>
                ))}
              </ul>

              <Button asChild variant="brand" size="lg" className="mt-8 w-fit">
                <a href="#hero-form">
                  Build my ATS resume
                  <ArrowRight className="size-4" />
                </a>
              </Button>
            </div>

            <div className="relative min-h-96 border-t border-brand/10 p-6 sm:p-10 lg:border-l lg:border-t-0">
              <div
                className="pointer-events-none absolute inset-0 bg-grid opacity-70"
                aria-hidden="true"
              />
              <div className="relative mx-auto flex h-full max-w-lg items-center">
                <div className="w-full rounded-2xl border border-border/80 bg-background/90 p-5 shadow-2xl shadow-brand/10 backdrop-blur sm:p-7">
                  <div className="flex items-center justify-between border-b border-border/70 pb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex size-10 items-center justify-center rounded-xl bg-brand/10 text-brand">
                        <ShieldCheck className="size-5" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">ATS check complete</p>
                        <p className="text-xs text-muted-foreground">Senior Product Designer</p>
                      </div>
                    </div>
                    <span className="rounded-full bg-success/10 px-2.5 py-1 text-xs font-medium text-success">
                      Ready
                    </span>
                  </div>

                  <div className="mt-5 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl border border-border/70 bg-muted/40 p-4">
                      <FileText className="size-5 text-brand" />
                      <p className="mt-4 text-sm font-semibold">Readable structure</p>
                      <div className="mt-3 space-y-2">
                        <span className="block h-1.5 w-full rounded-full bg-border" />
                        <span className="block h-1.5 w-4/5 rounded-full bg-border" />
                        <span className="block h-1.5 w-3/5 rounded-full bg-border" />
                      </div>
                    </div>
                    <div className="rounded-xl border border-brand/20 bg-brand/5 p-4">
                      <ScanSearch className="size-5 text-brand" />
                      <p className="mt-4 text-sm font-semibold">Matched keywords</p>
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {["Figma", "Research", "SaaS"].map((skill) => (
                          <span
                            key={skill}
                            className="rounded-md bg-brand/10 px-2 py-1 text-[11px] font-medium text-brand"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-3 rounded-xl border border-success/20 bg-success/5 p-4">
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
                      <Check className="size-4" />
                    </span>
                    <div>
                      <p className="text-sm font-semibold">Ready for the ATS</p>
                      <p className="text-xs text-muted-foreground">Clear and easy to parse</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
