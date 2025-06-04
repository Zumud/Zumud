import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRightIcon, PlayIcon } from "lucide-react";

interface HeroSectionProps {
  onAuthModalOpen?: (mode?: 'login' | 'signup') => void;
}

export default function HeroSection({ onAuthModalOpen }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden py-16 md:py-24 lg:py-32 bg-gradient-to-b from-white to-blue-50 dark:from-gray-950 dark:to-blue-950">
      {/* Decorative elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-48 w-48 md:h-64 md:w-64 rounded-full bg-blue-200/30 blur-3xl dark:bg-blue-900/30"></div>
        <div className="absolute right-1/4 bottom-1/3 h-64 w-64 md:h-96 md:w-96 rounded-full bg-purple-200/30 blur-3xl dark:bg-purple-900/30"></div>
      </div>

      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="grid gap-8 lg:gap-12 lg:grid-cols-2 xl:grid-cols-[1.2fr_0.8fr] items-center">
          <div className="flex flex-col justify-center space-y-6 lg:space-y-8">
            <div className="space-y-4 lg:space-y-6">
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent leading-tight">
                Instant job-specific resumes
              </h1>
              <p className="text-base md:text-lg lg:text-xl text-gray-500 dark:text-gray-400 max-w-[600px]">
                Get tailored resumes and cover letters for each job application in seconds. Our users report 3× more interviews — and save 15+ minutes per application.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:gap-4">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700"
                onClick={() => onAuthModalOpen?.('signup')}
              >
                Get Started Free
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-blue-200 dark:border-blue-800"
                onClick={() => onAuthModalOpen?.('login')}
              >
                <PlayIcon className="mr-2 h-4 w-4" />
                See a Demo
              </Button>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-6 space-y-2 sm:space-y-0 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center">
                <svg
                  className="mr-2 h-4 w-4 fill-current text-blue-500 flex-shrink-0"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>No credit card required</span>
              </div>
              <div className="flex items-center">
                <svg
                  className="mr-2 h-4 w-4 fill-current text-blue-500 flex-shrink-0"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>
          <div className="relative flex items-center justify-center">
            <div className="relative w-full max-w-[300px] sm:max-w-[350px] lg:max-w-[400px] overflow-hidden rounded-2xl border border-blue-100 bg-white shadow-xl dark:border-blue-800 dark:bg-gray-900">
              <div className="p-4 sm:p-6">
                <div className="mb-3 sm:mb-4 h-2 w-16 sm:w-20 rounded-full bg-blue-100 dark:bg-blue-800"></div>
                <div className="mb-4 sm:mb-6 h-3 sm:h-4 w-3/4 rounded-full bg-blue-100 dark:bg-blue-800"></div>
                <div className="space-y-2 sm:space-y-3">
                  <div className="h-2 sm:h-3 w-full rounded-full bg-gray-100 dark:bg-gray-800"></div>
                  <div className="h-2 sm:h-3 w-5/6 rounded-full bg-gray-100 dark:bg-gray-800"></div>
                  <div className="h-2 sm:h-3 w-4/6 rounded-full bg-gray-100 dark:bg-gray-800"></div>
                </div>
                <div className="mt-4 sm:mt-6 space-y-2 sm:space-y-3">
                  <div className="h-2 sm:h-3 w-full rounded-full bg-blue-50 dark:bg-blue-900"></div>
                  <div className="h-2 sm:h-3 w-5/6 rounded-full bg-blue-50 dark:bg-blue-900"></div>
                  <div className="h-2 sm:h-3 w-4/6 rounded-full bg-blue-50 dark:bg-blue-900"></div>
                </div>
                <div className="mt-4 sm:mt-6">
                  <div className="h-6 sm:h-8 w-1/3 rounded-full bg-gradient-to-r from-blue-600 to-violet-600"></div>
                </div>
              </div>
            </div>
            {/* Decorative cards - hidden on small screens to prevent overflow */}
            <div className="hidden xl:block absolute -left-6 -z-10 h-full w-full rounded-2xl border border-blue-100 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/50"></div>
            <div className="hidden xl:block absolute -left-12 -z-20 h-full w-full rounded-2xl border border-violet-100 bg-violet-50/50 dark:border-violet-900 dark:bg-violet-950/50"></div>
          </div>
        </div>
      </div>
    </section>
  );
} 