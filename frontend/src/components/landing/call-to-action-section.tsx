import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRightIcon } from "lucide-react";

interface CallToActionSectionProps {
  onAuthModalOpen?: (mode?: 'login' | 'signup') => void;
}

export default function CallToActionSection({ onAuthModalOpen }: CallToActionSectionProps) {
  return (
    <section className="py-20 bg-gradient-to-r from-blue-600 to-violet-600 text-white">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-6">
            Ready to Land Your Dream Job?
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Join thousands of professionals who have transformed their careers
            with AI-powered resume optimization. Start creating resumes that get
            you hired today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 font-semibold px-8 py-4 text-lg"
              onClick={() => onAuthModalOpen?.('signup')}
            >
              Get Started Free
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg"
              asChild
            >
              <Link href="#demo">
                Watch Demo
              </Link>
            </Button>
          </div>
          <div className="mt-8 flex items-center justify-center space-x-6 text-sm text-blue-100">
            <div className="flex items-center">
              <svg
                className="mr-2 h-4 w-4 fill-current"
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
              <span>Free trial • No credit card required</span>
            </div>
            <div className="flex items-center">
              <svg
                className="mr-2 h-4 w-4 fill-current"
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
              <span>Setup in 2 minutes</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
} 