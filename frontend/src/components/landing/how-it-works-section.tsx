import { FileTextIcon, ClipboardIcon, RocketIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function HowItWorksSection() {
  const steps = [
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
          {steps.map((step, index) => (
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

        <div className="mt-16 flex justify-center">
          <div className="relative rounded-2xl overflow-hidden border border-blue-100 dark:border-blue-800 shadow-lg">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-violet-500/10 dark:from-blue-500/5 dark:to-violet-500/5"></div>
            <div className="relative p-8 md:p-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
              <div className="grid gap-6 md:grid-cols-2 items-center">
                <div>
                  <h3 className="text-2xl font-bold mb-4">
                    Ready to transform your job search?
                  </h3>
                  <p className="text-muted-foreground mb-6">
                    Join thousands of job seekers who have increased their
                    interview rates by using Zumud&apos;s AI-powered resume
                    tailoring.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button 
                      className="bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700"
                      asChild
                    >
                      <Link href="/auth/signup">
                        Try for Free
                      </Link>
                    </Button>
                    <Button 
                      variant="outline"
                      className="border-gray-200 dark:border-gray-700"
                      asChild
                    >
                      <Link href="#demo">
                        Watch Demo
                      </Link>
                    </Button>
                  </div>
                </div>
                <div className="relative">
                  <div className="aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="rounded-full bg-white/90 dark:bg-gray-900/90 p-4 shadow-lg">
                        <svg
                          className="h-12 w-12 text-blue-600 dark:text-blue-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>
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