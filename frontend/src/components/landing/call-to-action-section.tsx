import { Button } from "@/components/ui/button";
import { ArrowRightIcon, CheckCircle2 } from "lucide-react";

interface CallToActionSectionProps {
  onAuthModalOpen?: (mode?: "login" | "signup") => void;
}

export default function CallToActionSection({ onAuthModalOpen }: CallToActionSectionProps) {
  return (
    <section className="section">
      <div className="container-page">
        <div className="bg-brand-gradient relative overflow-hidden rounded-3xl px-6 py-14 text-center shadow-xl shadow-brand/20 md:px-12 md:py-20">
          {/* Decorative glow */}
          <div
            className="pointer-events-none absolute inset-0 opacity-60"
            style={{
              background:
                "radial-gradient(28rem 28rem at 15% 10%, rgba(255,255,255,0.18), transparent 60%), radial-gradient(28rem 28rem at 85% 90%, rgba(255,255,255,0.12), transparent 60%)",
            }}
            aria-hidden="true"
          />

          <div className="relative mx-auto max-w-2xl">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">
              Ready to land your dream job?
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-lg leading-relaxed text-white/85">
              Join professionals who land more interviews with AI-tailored resumes.
              Your first 10 are on us.
            </p>

            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button
                size="xl"
                onClick={() => onAuthModalOpen?.("signup")}
                className="w-full bg-white font-semibold text-[var(--brand)] shadow-lg hover:bg-white/90 sm:w-auto"
              >
                Get started free
                <ArrowRightIcon className="size-5" />
              </Button>
              <Button
                size="xl"
                variant="outline"
                onClick={() => onAuthModalOpen?.("login")}
                className="w-full border-white/40 bg-white/10 text-white backdrop-blur hover:bg-white/20 hover:text-white sm:w-auto dark:bg-white/10"
              >
                Sign in
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-white/85">
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="size-4" />
                Free to start, no card
              </span>
              <span className="inline-flex items-center gap-1.5">
                <CheckCircle2 className="size-4" />
                Ready in under a minute
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
