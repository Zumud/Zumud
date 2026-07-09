import React from "react";
import {
  BrainIcon,
  ClockIcon,
  DownloadIcon,
  FileCode2,
  FileTextIcon,
  MessageSquareIcon,
  RefreshCwIcon,
  ScanText,
} from "lucide-react";

const FEATURES = [
  {
    icon: BrainIcon,
    title: "AI resume tailoring",
    description: "Rewrites your resume around the job post.",
    tint: "brand",
  },
  {
    icon: ScanText,
    title: "ATS friendly formatting",
    description: "Clean structure that is easy to scan.",
    tint: "violet",
  },
  {
    icon: ClockIcon,
    title: "Fast generation",
    description: "Get a tailored resume in about 30 seconds.",
    tint: "orange",
  },
  {
    icon: FileTextIcon,
    title: "Cover letters",
    description: "Create matching cover letters from the same job post.",
    tint: "violet",
  },
  {
    icon: MessageSquareIcon,
    title: "Application answers",
    description: "Generate strong answers for job application questions.",
    tint: "brand",
  },
  {
    icon: RefreshCwIcon,
    title: "Easy refinements",
    description: "Make it shorter, sharper, more formal, or keyword focused.",
    tint: "brand",
  },
  {
    icon: DownloadIcon,
    title: "PDF export",
    description: "Download a polished resume ready to send.",
    tint: "violet",
  },
  {
    icon: FileCode2,
    title: "LaTeX and Overleaf",
    description: "Export the source or open it in Overleaf.",
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
            Everything you need to apply faster
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Turn one resume into the right resume for each job.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
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
