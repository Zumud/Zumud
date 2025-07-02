import React from "react";
import { 
  BrainIcon, 
  FileTextIcon, 
  ClockIcon 
} from "lucide-react";

// Move features array outside component to prevent recreation on every render
const FEATURES = [
  {
    icon: <BrainIcon className="h-8 w-8 text-blue-500" />,
    title: "AI-Powered Tailoring",
    description:
      "Our advanced AI analyzes job descriptions and optimizes your resume to match specific requirements and keywords.",
  },
  {
    icon: <FileTextIcon className="h-8 w-8 text-violet-500" />,
    title: "ATS Optimization",
    description:
      "Get past Applicant Tracking Systems with resumes formatted and optimized for maximum compatibility.",
  },
  {
    icon: <ClockIcon className="h-8 w-8 text-red-500" />,
    title: "Lightning Fast",
    description:
      "Generate a perfectly tailored resume in 30 seconds. No more hours spent customizing applications.",
  },
];

function FeaturesSection() {
  return (
    <section id="features" className="py-20 bg-white dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Features That Get You Hired
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            All the tools you need to create compelling resumes that stand out
            from the crowd and land you more interviews.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FEATURES.map((feature, index) => (
            <div
              key={index}
              className="group relative p-6 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 hover:shadow-lg transition-all duration-300 hover:border-blue-200 dark:hover:border-blue-800"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-900/20 mb-4 group-hover:scale-110 transition-transform duration-300">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Memoize the component to prevent unnecessary re-renders
export default React.memo(FeaturesSection); 