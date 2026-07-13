import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import Footer from "@/components/landing/footer";
import { getGuides } from "@/lib/guides";

export const metadata: Metadata = {
  title: "Guides",
  description:
    "Practical, sourced guides on resume tailoring, ATS-friendly formatting, and getting more interviews.",
  alternates: { canonical: "https://zumud.com/guides" },
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function GuidesIndexPage() {
  const guides = getGuides();

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

          <h1 className="mt-6 text-3xl font-bold tracking-tight sm:text-4xl">
            Guides
          </h1>
          <p className="mt-3 text-muted-foreground">
            Practical, sourced advice on resumes, ATS, and getting more
            interviews.
          </p>

          <div className="mt-10 space-y-6">
            {guides.map((guide) => (
              <Link
                key={guide.slug}
                href={`/guides/${guide.slug}`}
                className="surface block p-6 transition-colors hover:border-brand/30"
              >
                <h2 className="text-xl font-semibold">{guide.title}</h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  {guide.description}
                </p>
                <p className="mt-3 text-xs text-muted-foreground">
                  Updated {formatDate(guide.dateModified)}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
