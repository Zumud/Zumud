import {
  BadgeCheck,
  Crosshair,
  ScanText,
} from "lucide-react";

const PROBLEMS = [
  {
    icon: ScanText,
    title: "Reads the job post",
    description: "Finds what matters.",
  },
  {
    icon: Crosshair,
    title: "Tailors your content",
    description: "Leads with what fits.",
  },
  {
    icon: BadgeCheck,
    title: "Keeps it honest",
    description: "Uses only your experience.",
  },
];

export default function ProblemSection() {
  return (
    <section id="problem" className="section scroll-mt-20 border-y border-border/60 bg-muted/30">
      <div className="container-page">
        <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="max-w-xl">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Generic resumes get ignored
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              Each role is different. Your resume should be too.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {PROBLEMS.map((problem) => {
              const Icon = problem.icon;
              return (
                <article
                  key={problem.title}
                  className="surface group p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-md"
                >
                  <div className="mb-5 flex items-center justify-between">
                    <div className="flex size-10 items-center justify-center rounded-xl bg-brand/10 text-brand">
                      <Icon className="size-5" />
                    </div>
                  </div>
                  <h3 className="font-semibold">{problem.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {problem.description}
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
