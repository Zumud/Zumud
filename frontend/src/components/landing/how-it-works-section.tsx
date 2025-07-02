import React from "react";
import { FileTextIcon, ClipboardIcon, RocketIcon } from "lucide-react";

// Move steps array outside component to prevent recreation on every render
const STEPS = [
  {
    icon: <FileTextIcon className="h-10 w-10 text-blue-500" />,
    title: "Upload your resume",
    description:
      "Start by uploading your existing resume or create a new one from scratch using our templates.",
  },
  {
    icon: <ClipboardIcon className="h-10 w-10 text-violet-500" />,
    title: "Paste the job description",
    description:
      "Add the job description you're applying for. Our AI will analyze the key requirements and skills needed.",
  },
  {
    icon: <RocketIcon className="h-10 w-10 text-indigo-500" />,
    title: "Receive your tailored resume",
    description:
      "Within minutes, get a professionally tailored resume optimized for the specific job you want.",
  },
];

function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="py-20 bg-gradient-to-b from-white to-blue-50 dark:from-gray-950 dark:to-blue-950"
    >
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Our simple three-step process helps you create the perfect resume
            for each job application in minutes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          {STEPS.map((step, index) => (
            <div
              key={index}
              className="relative flex flex-col items-center text-center p-6 rounded-xl bg-white dark:bg-gray-900 shadow-sm border border-gray-100 dark:border-gray-800 hover:shadow-md transition-shadow"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20 mb-4">
                {step.icon}
              </div>
              <div className="absolute -top-3 -left-3 flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-violet-600 text-white font-medium">
                {index + 1}
              </div>
              <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
              <p className="text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Memoize the component to prevent unnecessary re-renders
export default React.memo(HowItWorksSection); 