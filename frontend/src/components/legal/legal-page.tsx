import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import Footer from "@/components/landing/footer";

interface LegalSection {
  heading: string;
  paragraphs: string[];
}

interface LegalPageProps {
  title: string;
  lastUpdated: string;
  intro: string;
  sections: LegalSection[];
}

/**
 * Shared, theme-aware layout for static legal pages (privacy, terms, cookies).
 * Kept intentionally simple; content is placeholder copy the team can refine.
 */
export default function LegalPage({ title, lastUpdated, intro, sections }: LegalPageProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="container-page flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center" aria-label="Zumud home">
            <img src="/logos/zumud/combined.svg" alt="Zumud" className="h-7 w-auto" />
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="flex-1">
        <div className="container-page max-w-3xl py-12 md:py-16">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to home
          </Link>

          <h1 className="mt-6 text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">Last updated: {lastUpdated}</p>

          <p className="mt-6 text-base leading-relaxed text-muted-foreground">{intro}</p>

          <div className="mt-10 space-y-10">
            {sections.map((section) => (
              <section key={section.heading}>
                <h2 className="text-xl font-semibold">{section.heading}</h2>
                <div className="mt-3 space-y-3">
                  {section.paragraphs.map((p, i) => (
                    <p key={i} className="leading-relaxed text-muted-foreground">
                      {p}
                    </p>
                  ))}
                </div>
              </section>
            ))}
          </div>

          <div className="mt-12 rounded-2xl border border-border/60 bg-muted/40 p-6 text-sm text-muted-foreground">
            Questions about this policy? Email us at{" "}
            <a className="font-medium text-brand hover:underline" href="mailto:support@zumud.com">
              support@zumud.com
            </a>
            .
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
