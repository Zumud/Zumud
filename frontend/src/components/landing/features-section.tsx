import React from "react";
import { BrainIcon, FileTextIcon, ClockIcon, TargetIcon, MessageSquareIcon, RefreshCwIcon } from "lucide-react";

const FEATURES = [
  {
    icon: BrainIcon,
    title: "AI-powered tailoring",
    description:
      "Zumud analyzes each job description and rewrites your resume to match the exact skills and keywords recruiters look for.",
    tint: "brand",
  },
  {
    icon: FileTextIcon,
    title: "ATS optimization",
    description:
      "Clean, parseable formatting that sails through Applicant Tracking Systems so a human actually sees your application.",
    tint: "violet",
  },
  {
    icon: ClockIcon,
    title: "Lightning fast",
    description:
      "Generate a perfectly tailored resume in about 30 seconds. No more hours spent rewriting for every role.",
    tint: "orange",
  },
  {
    icon: MessageSquareIcon,
    title: "Cover letters & answers",
    description:
      "Generate matching cover letters and tailored answers to application questions from the same job description.",
    tint: "violet",
  },
  {
    icon: RefreshCwIcon,
    title: "Refine in one click",
    description:
      "Make it shorter, more formal, or add keywords. Iterate on any document with simple natural-language edits.",
    tint: "brand",
  },
  {
    icon: TargetIcon,
    title: "Built for results",
    description:
      "Every output is focused on one goal: getting you more interviews for the jobs you actually want.",
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
            All the tools to create compelling, job-specific applications that
            stand out and land more interviews.
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
