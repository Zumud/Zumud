import React from "react";
import { BrainIcon, FileTextIcon, ClockIcon, DownloadIcon, MessageSquareIcon, RefreshCwIcon } from "lucide-react";

const FEATURES = [
  {
    icon: BrainIcon,
    title: "AI-powered tailoring",
    description: "We rewrite your resume to match each job's skills and keywords.",
    tint: "brand",
  },
  {
    icon: FileTextIcon,
    title: "ATS optimization",
    description: "Clean formatting that gets you past the bots to a human.",
    tint: "violet",
  },
  {
    icon: ClockIcon,
    title: "Lightning fast",
    description: "A tailored resume in about 30 seconds, not an afternoon.",
    tint: "orange",
  },
  {
    icon: MessageSquareIcon,
    title: "Cover letters & answers",
    description: "Matching cover letters and application answers from the same job post.",
    tint: "violet",
  },
  {
    icon: RefreshCwIcon,
    title: "Refine in one click",
    description: "Shorter, more formal, more keywords. Edit in plain English.",
    tint: "brand",
  },
  {
    icon: DownloadIcon,
    title: "Export anywhere",
    description: "Download as PDF, export the LaTeX, or open it in Overleaf.",
    tint: "orange",
  },
];

const TINTS: Record<string, string> = {
  brand: "bg-brand/10 text-brand ring-brand/15",
  violet: "bg-[var(--accent2)]/10 text-[var(--accent2)] ring-[var(--accent2)]/15",
  orange: "bg-[#FF6B35]/10 text-[#e85d2c] ring-[#FF6B35]/15 dark:text-[#ff8a5e]",
};

function FeaturesSection() {
  return (
    <section id="features" className="section scroll-mt-20 bg-muted/30">
      <div className="container-page">
        <div className="mx-auto mb-14 max-w-2xl text-center">
          <span className="badge-soft mb-4">Features</span>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need to get hired
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            One resume becomes the right resume for every job.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="surface surface-hover group p-6"
              >
                <div
                  className={`mb-4 flex size-12 items-center justify-center rounded-xl ring-1 transition-transform duration-300 group-hover:scale-110 ${TINTS[feature.tint]}`}
                >
                  <Icon className="size-6" />
                </div>
                <h3 className="mb-2 text-lg font-semibold transition-colors group-hover:text-brand">
                  {feature.title}
                </h3>
                <p className="leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default React.memo(FeaturesSection);
