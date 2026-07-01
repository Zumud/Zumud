import React from "react";
import { FileTextIcon, ClipboardIcon, RocketIcon } from "lucide-react";

const STEPS = [
  {
    icon: FileTextIcon,
    title: "Add your resume",
    description: "Upload a PDF or paste your text. No account needed.",
  },
  {
    icon: ClipboardIcon,
    title: "Paste the job post",
    description: "Zumud finds the key skills, keywords, and role requirements.",
  },
  {
    icon: RocketIcon,
    title: "Download your tailored resume",
    description: "Get an ATS friendly PDF built for that role in about 30 seconds.",
  },
];

function HowItWorksSection() {
  return (
    <section id="how-it-works" className="section scroll-mt-20">
      <div className="container-page">
        <div className="mx-auto mb-14 max-w-2xl text-center">
          <span className="badge-soft mb-4">How it works</span>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Three steps. One better resume.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Minutes per application, not hours.
          </p>
        </div>

        <div className="relative grid grid-cols-1 gap-6 md:grid-cols-3 lg:gap-8">
          {/* Connecting line on desktop */}
          <div
            className="absolute left-0 right-0 top-9 hidden h-px bg-gradient-to-r from-transparent via-border to-transparent md:block"
            aria-hidden="true"
          />

          {STEPS.map((step, index) => {
            const Icon = step.icon;
            return (
              <div
                key={index}
                className="surface surface-hover relative flex flex-col items-center p-7 text-center"
              >
                <div className="relative mb-5">
                  <div className="flex size-16 items-center justify-center rounded-2xl bg-brand/10 text-brand ring-1 ring-brand/15">
                    <Icon className="size-7" />
                  </div>
                  <span className="absolute -right-2 -top-2 flex size-7 items-center justify-center rounded-full bg-brand-gradient text-xs font-bold text-white shadow-sm">
                    {index + 1}
                  </span>
                </div>
                <h3 className="mb-2 text-xl font-semibold">{step.title}</h3>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default React.memo(HowItWorksSection);
